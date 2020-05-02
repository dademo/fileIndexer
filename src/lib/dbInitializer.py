from public import FileHandleModule

from sqlalchemy import MetaData
from sqlalchemy.engine import Engine, Connection, Transaction

from typing import List
import os


def is_sqlite(dbEngine: Engine):
    return dbEngine.url.drivername == 'sqlite'
    #return str(dbEngine.url).startswith('sqlite')

def initializeDb(dbEngine: Engine, modules: List[FileHandleModule], configuration: dict) -> None:
    
    for module in modules:
        # We ensure the schema will not have path separator
        schema = module.getDatabaseSchema().replace(os.path.sep, '_')
        if is_sqlite(dbEngine):
            ensure_sqlite_schema(dbEngine, schema)
        else:
            ensure_schema(dbEngine, schema)

        moduleMetaData = MetaData(schema=schema)
        module.defineTables(moduleMetaData, configuration)

        globalMetaData = sqlalchemy_merge_metaDatas([ moduleMetaData ])
        globalMetaData.create_all(dbEngine)
        
def sqlalchemy_merge_metaDatas(metaDatas: List[MetaData]):

    mergedMetaDatas = MetaData()

    for metaData in metaDatas:
        for (table_name, table) in metaData.tables.items():
            mergedMetaDatas._add_table(table_name, table.schema, table)

    return mergedMetaDatas


def ensure_sqlite_schema(dbEngine: Engine, schema: str) -> None:

    def db_dirname_from_engine():
        return os.path.dirname(dbEngine.url.database) or '.'


    with dbEngine.begin() as dbConnection:
        try:
            next(filter(lambda x: x['name'] == schema, dbConnection.execute('PRAGMA DATABASE_LIST').fetchall()))
        except StopIteration:

            dbConnection.execute('''ATTACH DATABASE '%(databasePath)s' AS "%(schema)s"''' % {
                'databasePath': os.path.join(db_dirname_from_engine(), '%s.db' % schema),
                'schema': schema
            })

def ensure_schema(dbEngine: Engine, schema: str) -> None:

    with dbEngine.begin() as dbConnection:
        dbConnection.execute('''
            CREATE SCHEMA IF NOT EXISTS %(schema)s
        ''' % { 'schema': schema })