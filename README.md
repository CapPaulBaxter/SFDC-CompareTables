# SFDC-CompareTables

A sketch of a script to compare tables between two salesforce orgs, the collection `tablesForComparison` is initilaised with a list of sobjects to retrieve, a key to compare them by (may be a single field or an ordered collection of fields) along with a `whereClause` to optionally filter out records for comparison.

`instancesToCompare` should contain the login credentials to two salesforce orgs, the assumption is that the first entry is the location of any changes, and the second is the org to bring into line with the first, a dev org and then a production org is probably typical usage.

When executed the script will query for all creatable fields in the table in either org, dervice a set of common fields and export both tables to csv files.

# Example output 

Running against `product2` the output might look like:

```
8418 rows in Product2 instance 0
8386 rows in Product2 instance 1
identical 4117
missing 32
mismatches 4269
mismatchTypes:
- column ('Layout__c',) 3339
- column ('CurrencyIsoCode', 'Layout__c') 341
- column ('CurrencyIsoCode',) 222
- column ('Layout__c', 'SortOrder__c') 216
- column ('CurrencyIsoCode', 'RecordTypeId') 3
- column ('CurrencyIsoCode', 'RecordTypeId', 'Layout__c') 2
- column ('ConfigurationType__c',) 1
- column ('Description',) 1
```

Meaning that the dev org has 8418 records while the production org has 8386, 4117 are identical across both orgs, and 32 only exist in the development org.

The listing of mismatch types lists the columns that the records mismatch on most often, in this example the majority of the mismatches are due to variations in a single field `Layout__c`, the next most common mismatch is that records mismatch on BOTH `CurrencyIsoCode` and `Layout__c` 

The mismatch reasons identified are unique causes for mismatches so if a record is counted as a mismatch in ('CurrencyIsoCode', 'Layout__c') it is not also double counted in the mismatches under ('Layout__c',)
