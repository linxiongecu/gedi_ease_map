#!/usr/bin/env python3

DESCRIPTION='''
Export subsets of GEDI footprint files to CSV or GeoJSON

University of Maryland
John Armston
'''

import os
import sys
import re
import h5py
import numpy
import pandas
import geopandas
import argparse
import datetime

from osgeo import ogr

import pygeos
from pygeos import box
from pygeos import Geometry
from pygeos import contains
from pygeos import points

try:
    import psycopg2
    DB_CONNECTION = "host='gsapp11.clust.gshpc.umd.edu' dbname='gedicalval' user='gedisftp' password='laser'"
    SOC_ROOT = os.path.join(os.sep,'gpfs','data1','vclgp','data','iss_gedi','soc')
    HAS_PSYCOPG2 = True
except ModuleNotFoundError:
    HAS_PSYCOPG2 = False


def get_polygons_from_kml(kml_file):
    driver = ogr.GetDriverByName('KML')
    dataSource = driver.Open(kml_file)
    if dataSource is None:
        print('Could not open {}'.format(kml_file))
        exit(1)
    result = []
    number_of_layers = dataSource.GetLayerCount()
    for layer_id in range(number_of_layers):
        layer = dataSource.GetLayerByIndex(layer_id)
        for feat in layer:
            featgeom = feat.GetGeometryRef()
            if featgeom.GetGeometryName() != 'GEOMETRYCOLLECTION':
                geom_wkt = featgeom.ExportToWkt()
                geom = Geometry(geom_wkt)
                result.append(geom)
    return result


def get_dates_from_mission_weeks(start_mw, end_mw):
    first_mw_date = datetime.datetime.strptime('2018-12-13', '%Y-%m-%d')
    start_mw_offset = (start_mw - 1) * 7
    start_mw_date = first_mw_date + datetime.timedelta(start_mw_offset)
    end_mw_offset = (end_mw - 1) * 7 + 6
    end_mw_date = first_mw_date + datetime.timedelta(end_mw_offset)
    start_time = start_mw_date.strftime('%Y-%m-%d')
    end_time = end_mw_date.strftime('%Y-%m-%d')
    return start_time, end_time


class GEDIH5File:
    def __init__(self, filename):
        self.filename = filename
        self.filename_pattern = re.compile(r'GEDI0(1|2|4)_(A|B)_(\d{13})_O(\d{5})_(\d{2})_T(\d{5})_(\d{2})_(\d{3})_(\d{2})_V002((?:_10algs|))\.h5')
        if self.is_valid_filename():
            self.release = 2
        else:
            self.filename_pattern = re.compile(r'GEDI0(1|2|4)_(A|B)_(\d{13})_O(\d{5})_T(\d{5})_(\d{2})_(\d{3})_(\d{2})\.h5')
            if self.is_valid_filename():
                self.release = 1
            else:
                raise ValueError('invalid GEDI filename: "{}"'.format(self.filename))

    def is_valid(self):
        return self.is_valid_filename() and h5py.is_hdf5(self.filename)

    def is_valid_filename(self):
        m = self.filename_pattern.fullmatch(os.path.basename(self.filename))
        if m:
            return True
        else:
            return False

    def get_orbit_number(self):
        m = self.filename_pattern.fullmatch(os.path.basename(self.filename))
        if m:
            return int(m.group(4))
        else:
            raise ValueError('invalid GEDI filename: "{}"'.format(self.filename))

    def get_granule_number(self):
        m = self.filename_pattern.fullmatch(os.path.basename(self.filename))
        if m:
            if self.release == 2:
                return int(m.group(5))
            else:
                return 1
        else:
            raise ValueError('invalid GEDI filename: "{}"'.format(self.filename))

    def get_product_id(self):
        m = self.filename_pattern.fullmatch(os.path.basename(self.filename))
        if m:
            return '{}{}'.format(m.group(1), m.group(2))
        else:
            raise ValueError('invalid GEDI filename: "{}"'.format(self.filename))

    def open(self):
        self.fid = h5py.File(self.filename, 'r')
        self.beams = [beam for beam in self.fid.keys() if beam.startswith('BEAM')]

    def close(self):
        self.fid.close()
        self.beams = None

    def get_shot_indices(self, beam_group, product_id, geom_list):
        if product_id in ('2A','4A'):
            x_name, y_name = 'lon_lowestmode', 'lat_lowestmode'
        elif product_id == '2B':
            x_name, y_name = 'geolocation/lon_lowestmode', 'geolocation/lat_lowestmode'
        else:
            x_name, y_name = 'geolocation/longitude_bin0', 'geolocation/latitude_bin0'

        shot_geoms = points(beam_group[x_name][()], y=beam_group[y_name][()])

        idx_extract = numpy.zeros(beam_group['shot_number'].size, dtype=numpy.bool)
        for geom in geom_list:
            mask = contains(geom, shot_geoms)
            idx_extract = idx_extract | mask
        
        return idx_extract

    def export_shots(self, beam, geom, dataset_list=[]):
        # Get the group information
        group = self.fid[beam]
        product_id = self.get_product_id()
        nshots = group['shot_number'].size

        # Find indices to extract
        idx_extract = self.get_shot_indices(group, product_id, geom)
        if not numpy.any(idx_extract):
            return
        tmp, = numpy.nonzero(idx_extract)
        idx_start = numpy.min(tmp)
        idx_finish = numpy.max(tmp) + 1
        idx_subset = idx_extract[idx_start:idx_finish]

        # Function to extract datasets for selected shots
        def get_selected_shots(name, obj):
            if isinstance(obj, h5py.Dataset):
                try:
                    shot_axis = obj.shape.index(nshots)
                    if obj.ndim == 1:
                        arr = obj[idx_start:idx_finish]
                        colnames = [name]
                    elif obj.ndim == 2:
                        if shot_axis == 0:
                            arr = obj[idx_start:idx_finish,...]
                        else:
                            arr = numpy.transpose(obj[...,idx_start:idx_finish])
                        colnames = ['{}_{:03d}'.format(name,i) for i in range(obj.shape[shot_axis-1])]
                    else:
                        print('{} is not a 1D or 2D dataset'.format(name))
                        raise
                    df = pandas.DataFrame(data=arr[idx_subset,...], columns=colnames)
                    if name == 'rh':
                        #print('df---i want rh98', df['rh_098'])
                        df = df['rh_098']
                    datasets.append(df)
                except ValueError:
                    print('{} is not a footprint level dataset'.format(name))
                    raise
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise

        # Extract and combine the data for extracted shots
        datasets = []
        for name in dataset_list:
            out_name = os.path.basename(name)
            get_selected_shots(out_name, group[name])
        outdata = pandas.concat(datasets, axis=1)
        #print(outdata.loc[outdata['quality_flag'] > 0], 'outdata is here')
        # I want to filter data Here
        outdata['lon_lowestmode'] = round(outdata['lon_lowestmode'], 5) 
        outdata['lat_lowestmode'] = round(outdata['lat_lowestmode'], 5)
        return outdata[['lon_lowestmode','lat_lowestmode', 'rh_098']]


class FileDatabase:
    def __init__(self, release=2, rootpath=SOC_ROOT):
        self.file_by_orbit = {}
        self.rootpath = rootpath
        self.release = release
        if self.release == 2:
            self.tablename = 'l1_data_mw'
        else:
            self.tablename = 'l1_r001_mw'

    def query_file_list(self, product, level, type, pgeversion, start, end, geomlist):
        for geom in geomlist:
            tmp = """SET constraint_exclusion = on; 
                     SELECT DISTINCT ON (r.orbit,r.granule) 
                     r.filename, r.year, r.doy, r.orbit, r.granule
                     FROM 
                     (SELECT (a.shotnumber / 10000000000000)::integer AS orbit,
                             (MOD(a.shotnumber, 100000000000) / 100000000)::integer AS granule,
                              a.time,a.geom FROM 
                     (SELECT shotnumber,time,geom 
                     FROM gedi_footprints.{} 
                     WHERE time >= %s AND time < %s) a 
                     WHERE ST_Within(a.geom, ST_GeomFromText(%s,0))) b 
                     INNER JOIN gedi_data.orbit_h5_files r ON r.orbit = b.orbit 
                     WHERE r.product = %s AND r.level = %s AND r.type = %s AND r.pgeversion = %s 
                     ORDER BY r.orbit ASC, r.granule ASC, r.generation DESC, r.extra DESC;""".format(self.tablename)

            args = (start, end, pygeos.io.to_wkt(geom, rounding_precision=9), product, level, type, pgeversion)
            result = self._execute_query(tmp, args)
            for filename,year,doy,orbit,granule in result:
                h5filepath = os.path.join(self.rootpath, '{:04.0f}'.format(year),
                    '{:03.0f}'.format(doy), filename)
                if os.path.exists(h5filepath):
                    h5file = GEDIH5File(h5filepath)
                    if h5file.get_orbit_number() not in self.file_by_orbit:
                        self.file_by_orbit[h5file.get_orbit_number()] = {}
                    self.file_by_orbit[h5file.get_orbit_number()][h5file.get_granule_number()] = h5file

    def _execute_query(self, sql, args):
        con = psycopg2.connect(DB_CONNECTION)
        cursor = con.cursor()
        cursor.execute(sql, args)
        result = cursor.fetchall()
        cursor.close()
        con.close()
        return(result)

    def add_file_list(self, list_filename, start, end, geomlist):
        for geom in geomlist:
            sql = """SET constraint_exclusion = on;
                 SELECT DISTINCT r.orbit FROM 
                 (SELECT (a.shotnumber / 10000000000000)::integer AS orbit,a.time,a.geom FROM
                 (SELECT shotnumber,time,geom
                 FROM gedi_footprints.{}
                 WHERE time >= %s AND time < %s) a
                 WHERE ST_Within(a.geom, ST_GeomFromText(%s,0))) r;""".format(self.tablename)
            args = (start, end, pygeos.io.to_wkt(geom, rounding_precision=9))
            result = self._execute_query(sql, args)
            orbitlist = [o for o, in result]

        with open(list_filename, 'r') as fid:
            for line in fid:
                fn = line.rstrip('\n')
                h5file = GEDIH5File(fn)
                if h5file.get_orbit_number() in orbitlist:
                    if h5file.is_valid():
                        if h5file.get_orbit_number() not in self.file_by_orbit:
                            self.file_by_orbit[h5file.get_orbit_number()] = {}
                        self.file_by_orbit[h5file.get_orbit_number()][h5file.get_granule_number()] = h5file
                    else:
                        print('{} is not a valid GEDI H5 file'.format(fn))

    def get_file(self, orbit_number, granule_number=1):
        if orbit_number in self.file_by_orbit:
            return self.file_by_orbit[orbit_number][granule_number]
        else:
            return None


if __name__ == '__main__':
    # Parse command line arguments
    current_timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d')    
    argparser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    argparser.add_argument('output_file', metavar='FILE', type=str,
        help='Output file for selected shots')
    argparser.add_argument('-d', '--dataset-list', metavar='FILE', type=str,
        help='File containing datasets to copy (one per line)')
    argparser.add_argument('-f', '--file-list', metavar='FILE', type=str,
        help='File containing paths to the L1B/L2A/L2B files (one per line)')
    argparser.add_argument('-k', '--kml', metavar='FILE', type=str,
        help='KML file to define extent of subset')
    argparser.add_argument('-b', '--bbox', metavar='FLOAT', nargs=4, type=float,
        help='Geographic coordinate bounding box [minx maxy maxx miny]')
    argparser.add_argument('-o', '--out_format', default='CSV', choices=['CSV','ESRI Shapefile','GeoJSON','GPKG'],
        type=str, help='Output file format')
    argparser.add_argument('--release', metavar='INT', type=int, default=2, choices=[1,2],
        help='DAAC release number')
    if HAS_PSYCOPG2:
        argparser.add_argument('--root_path', default=SOC_ROOT, metavar='STR', 
            help='Root path to the GEDI h5 data files on the local file system')
        argparser.add_argument('--product', type=str, metavar='STR', default='GEDI02', choices=['GEDI01','GEDI02','GEDI04'],
            help='Product name')
        argparser.add_argument('--level', type=str, metavar='STR', default='A', choices=['A','B'],
            help='Product level')
        argparser.add_argument('--type', type=str, metavar='STR', default='02', choices=['01','02'],
            help='Product type (01=rapid,02=final)')
        argparser.add_argument('--pgeversion', metavar='INT', type=int, default=3,
            help='Product PGEVersion')
        argparser.add_argument("--start_time", type=str, metavar='DATE', default="2019-04-18",
            help='start time to use [%(default)s]')
        argparser.add_argument("--end_time", type=str, metavar='DATE', default=current_timestamp,
            help='end time to use [%(default)s]')
        argparser.add_argument('--mission_weeks', default=False, action="store_true",
            help='start_time and end_time are GEDI mission week numbers [%(default)s]')

    args = argparser.parse_args()

    # Load the subset geometry
    if args.bbox:
        geom_list = [box(args.bbox[0], args.bbox[3], args.bbox[2], args.bbox[1])]
    elif args.kml:
        geom_list = get_polygons_from_kml(args.kml)
    else:
        print('error: --bbox and --kml not specified.')
        exit(1)

    # Convert mission weeks to dates if necessary
    if args.mission_weeks:
        start_mw = int(args.start_time)
        end_mw = int(args.end_time)
        start_time, end_time = get_dates_from_mission_weeks(start_mw, end_mw)
        print('Date range for mission weeks {}-{} is {} to {} inclusive.'.format(start_mw, end_mw, start_time, end_time))
    else:
        start_time, end_time = args.start_time, args.end_time

    # Load file database
    file_database = FileDatabase(rootpath=args.root_path, release=args.release)
    if args.file_list:
        file_database.add_file_list(args.file_list, start_time, end_time, geom_list)
    else:
        if HAS_PSYCOPG2:
            file_database.query_file_list(args.product, args.level, args.type, args.pgeversion, start_time, end_time, geom_list)
        else:
            print('error: psycopg2 not found, database query unsupported. Install psycopg2 or specify the --file-list option.')
            exit(1)

    # Load dataset list
    dataset_list = []
    if args.dataset_list:
        with open(args.dataset_list) as fid_dataset_list:
            dataset_list = [line.strip() for line in fid_dataset_list.readlines() if len(line) > 1]
    else:
        print('error: --dataset_list not specified.')
        exit(1)
    
    # Loop through each h5 file and beam
    number_of_files = len(file_database.file_by_orbit)
    outdata_list = []
    for i,orbit in enumerate(file_database.file_by_orbit):
        for j,granule in enumerate(file_database.file_by_orbit[orbit]):
            h5file = file_database.get_file(orbit,granule_number=granule)
            if h5file:
                print('Subsetting {} ({}/{})'.format(h5file.filename, i+1, number_of_files), flush=True)
                h5file.open()
                for beam in h5file.beams:
                    outdata = h5file.export_shots(beam, geom_list, dataset_list=dataset_list)
                    outdata_list.append(outdata)
                h5file.close()

    # Concatenate the results
    if len(outdata_list) > 0:
        outdata = pandas.concat(outdata_list, axis=0)
    else:
        print('There are no intersecting shots')
        exit(1)

    # Output the data to file
    if args.out_format == 'CSV':
        outdata.to_csv(args.output_file, mode='w', header=True, index=False)
    else:
        if 'lon_lowestmode' in outdata.columns and 'lat_lowestmode' in outdata.columns:
            shot_geom = geopandas.points_from_xy(outdata.lon_lowestmode, outdata.lat_lowestmode)
        elif 'lon_highestreturn' in outdata.columns and 'lat_highestreturn' in outdata.columns:
            shot_geom = geopandas.points_from_xy(outdata.lat_highestreturn, outdata.lat_highestreturn)
        elif 'longitude_bin0' in outdata.columns and 'latitude_bin0' in outdata.columns:
            shot_geom = geopandas.points_from_xy(outdata.longitude_bin0, outdata.latitude_bin0)
        elif 'longitude_lastbin' in outdata.columns and 'latitude_lastbin' in outdata.columns:
            shot_geom = geopandas.points_from_xy(outdata.longitude_lastbin, outdata.latitude_lastbin)
        else:
            print('error: geometry columns needed for {} not specified in --dataset_list.')
            exit(1)
        gdf = geopandas.GeoDataFrame(outdata, geometry=shot_geom)      
        gdf.to_file(args.output_file, driver=args.out_format)


