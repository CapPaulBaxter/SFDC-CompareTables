
import sfdclib
from collections import namedtuple

def getColumnsForTableName(session,tableForComparison):
  pass

TableForComparison = namedtuple('TableForComparison', ['sobject', 'naturalKey', 'whereClause'])


tablesForComparison = [  
  TableForComparison(sobject='Product2', naturalKey=['ExternalId2__c'], whereClause='where Product_Type__c != \'Spare Parts\'')
]


instancesToCompare = [
  sfdclib.SfdcSession(username='username@domain.com',password='password1',is_sandbox=True,instance='development.org.my' ),
  sfdclib.SfdcSession(username='username@domain.com',password='password1',is_sandbox=False,instance='production.org.my' )
]

globalFieldsToSkipRetrieve = set()
globalFieldsToSkipComparison = set()



for table in tablesForComparison:

  allFields    = set()  
  commonFields = None

  for instanceInd,instance in enumerate(instancesToCompare):
    if not hasattr(instance,'restClient'):
      instance.login()
      instance.restClient = sfdclib.SfdcRestApi(instance)
      instance.bulkClient = sfdclib.SfdcBulkApi(instance)
      instance.fieldSets = {}

    fieldSet = instance.fieldSets.setdefault(table.sobject,set(['Id']))
    print('Desc call',instanceInd,instance.get_server_url(),table.sobject)
    for field in instance.restClient.get( '/sobjects/{}/describe/'.format(table.sobject)).get('fields'):
      if field['createable'] and field['name'] not in globalFieldsToSkipRetrieve:
        fieldSet.add(field['name'])
    for field in table.naturalKey:
      fieldSet.add(field)
    
    allFields.update(fieldSet)
    if commonFields is None:
      commonFields = set(fieldSet)
    else:
      commonFields = commonFields.intersection(fieldSet)
  print('commonFields:',len(commonFields),'uniqueFields:',len(allFields.difference(commonFields)) )

  for instanceInd,instance in enumerate(instancesToCompare):
    query = ', '.join(sorted(commonFields))
    orderClause = ', '.join(table.naturalKey)
    query = 'SELECT {} FROM {} {} order by {}'.format(query, table.sobject, table.whereClause, orderClause)
    print('Retrieve',instanceInd,instance.get_server_url(),table.sobject)
    open('temp_{}_.csv'.format(instanceInd),'wb').write(instance.bulkClient.export_object( table.sobject, query=query).encode('utf8') )


import unicodecsv as csv
for table in tablesForComparison:
  instanceMaps = {}
  for instanceInd,instance in enumerate(instancesToCompare):
    instanceMaps[instanceInd] = {}
    for row in csv.DictReader(open('temp_{}_.csv'.format(instanceInd),'rb')):
      key = []
      for field in table.naturalKey:
        key.append(row[field])
      if tuple(key) in instanceMaps[instanceInd]:
        print('instance',instanceInd,'Duplicate Key:',tuple(key),'Record Id',row['Id'])
      instanceMaps[instanceInd][tuple(key)] = row
  
  print(len(instanceMaps[0]),'rows in',table.sobject,'instance',0)
  print(len(instanceMaps[1]),'rows in',table.sobject,'instance',1)

  m0 = instanceMaps[0]
  m1 = instanceMaps[1]
  identical = 0
  missing = 0
  mismatches = 0
  mismatchTypes = {}

  for k,v in m0.items():
    if k not in m1:
      missing+=1
    elif v != m1[k]:
      hasMismatch = False

      r1,r2 = v,m1[k]
      mismatchingColumns = []

      for col,val in r1.items():
        if col != 'Id' and val != r2[col]:
          mismatchingColumns.append(col)

      if len(mismatchingColumns) > 0:
        mismatchingColumns = tuple(sorted(mismatchingColumns))
        cnt = mismatchTypes.setdefault(mismatchingColumns, 0)
        mismatchTypes[mismatchingColumns] = cnt+1
        hasMismatch = True

      if hasMismatch:
        mismatches += 1
      else:
        identical+=1
    else:
      identical+=1

  print('identical',identical)
  print('missing',missing)
  print('mismatches',mismatches)
  print('mismatchTypes:')
  for kind,count in sorted(mismatchTypes.items(),key=lambda x:x[1],reverse=True):
    print('- column',kind,count)

