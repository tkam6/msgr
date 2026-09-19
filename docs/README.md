# MESSENGER (tentative)

A simple and fast messaging application.

> [!Warning]
> Still in very early stages of development.

## Running from source

```console
git clone https://codeberg.org/vallu/msgr.git
cd ./msgr/
python3 -m pip venv ./.venv/
. ./.venv/bin/activate
python3 -m pip install -e ./
python3 -BOO ./src/main.py
```

## Building

Assuming the project has already been cloned and `cd`ed into:

```console
python3 -m venv ./.venv/
. ./.venv/bin/activate
python3 -m pip install -r ./build_requirements.txt
python3 -m pip install -e ./
python3 -BOO ./dev/pc.py
```
