## attack
To perform an SQL injection attack with payloads found in the `payloads/sqli` folder:

```
$ python3 brute.py attack --key first_name --url https://some.url/graphql --attack sqli --schema ../schema.json
```
Where `schema.json` is in the following format:
```
{
  "query": "mutation addActionContact(\n  $action: ActionInput!,\n  $contact:ContactInput!,\n  $contactRef:ID,\n  $actionPage:Int!,\n){\n  addActionContact(\n    actionPageId: $actionPage, \n    action: $action,\n    contactRef:$contactRef,\n    contact:$contact,\n  ){contactRef,firstName}\n  }\n",
  "variables": {
    "actionPage": 49,
    "action": {
      "actionType": "test",
      "fields": [{ "key": "test", "value": "test" }]
    },
    "contact": {
    "birthDate": "1970-01-01",
      "first_name": "test",
      "last_name": "aa",
      "email": "sdf@sdf",
      "nationality": {
        "country": "fr",
        "documentNumber": "1234",
        "documentType": "national.id.number"
      },
      "address": {
        "country": "pl",
        "postcode": "1234",
        "street": "123",
        "streetNumber": "12",
        "region": "PL",
        "locality": "Absnasd"
      }
    },
  },
  "operationName": "addActionContact"
}
```