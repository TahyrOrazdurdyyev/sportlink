# Установка GDAL для PostGIS на Windows

Для работы с геолокацией (PointField) нужен GDAL. Варианты:

## Вариант 1: OSGeo4W (рекомендуется)

1. Скачайте OSGeo4W: https://trac.osgeo.org/osgeo4w/
2. Установите GDAL пакет
3. Добавьте в PATH: `C:\OSGeo4W64\bin`

## Вариант 2: Conda

```bash
conda install -c conda-forge gdal
```

## Вариант 3: Временно без геолокации

Для быстрого старта можно временно заменить PointField на обычные поля lat/lng.

