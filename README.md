# Tap for CBX1


## Required Config Fields

```
{
    "access_token": "...",
    "organization_id": "...",
    "user_id": "..."
    ...
}
```

## Streams

Current supported streams are:
- Accounts
- Contacts

## Schemas

The stream schemas are hardcoded in each individual stream class

## Running this locally

1. Install dependencies with Poetry:
```
poetry install
```

2. Create a config.json with the required fields

3. Run a discover to generate a catalog.json

```
tap-cbx1 --config <path to config> --discover > <desired location for catalog>
```

4. Run a sync against the catalog.json

```
tap-cbx1 --config <path to config> --catalog <path to catalog> > <path to data output>
```
