import json as mjson
import sys
import re
import io
import os

class GeoJsonConvertor:
    DEFAULT_SRID = "SRID=4326"

    def __init__(self, jsonFile):
        self.jsonFile = jsonFile
        self.jsonContent = ""
        self.polygons = {}
        self.polygonsProperties = {}
        self.wktPolygons = []
        self.srid = self.DEFAULT_SRID

        with open(self.jsonFile, 'r') as file:
            fileContent = file.read()
            self.jsonContent = mjson.loads(fileContent)

        self.__initGeoJsonSrid()
        self.__initPolygons()

    def __initGeoJsonSrid(self):
        if "crs" in self.jsonContent:
            self.srid = "SRID=" + (self.jsonContent["crs"]["properties"]["name"]).split(":")[1]

    def __initPolygons(self):
        for i, polygon in enumerate(self.jsonContent["features"]):
            self.polygonsProperties[i] = polygon["properties"]
            self.polygons[i] = polygon["geometry"]

        if len(self.polygonsProperties) != len(self.polygons):
            raise Exception('Error: number of polygons propreties does not match polygons geometry')

        return self.polygons

    def getWktPolygons(self):

        for key, value in self.polygons.items():
            properties = mjson.dumps(self.polygonsProperties[key])

            if not value:
                continue

            coordinates = mjson.dumps(value["coordinates"])
            coordinatesWithoutCommaInBrackets = re.sub(r", (\d+.\d+)", " \\1", coordinates)
            wktCoordinates = re.sub(r"()\[|\]", "", coordinatesWithoutCommaInBrackets)

            self.wktPolygons.append([properties, self.srid + ";" + value['type'] + "(((" + wktCoordinates + ")))"])

        return self.wktPolygons


class FileGenerator:
    def __init__(self):
        print("Creating directory polygons")
        try:
            os.mkdir("./polygons")
        except FileExistsError:
            print("Directory polygons already existing")
            print("Continuing process...")

        self.dirPath = "./polygons"

    def generatePolygonsFiles(self, polygons):
        for i, polygon in enumerate(polygons):
            properties = polygon[0]
            geom = polygon[1]

            with open(f"{self.dirPath}/zone_{i}.txt", "w") as polyFile:
                separator = "="
                polyFile.write(f"{properties}\n")
                polyFile.write(f"{separator*50}\n")
                polyFile.write(geom)

        print("Files created.")


def init():
    if len(sys.argv[1:]) < 1:
        print("Missing arguments. command should look like this: python3 main.py [geoJsonFile]")
    else:
        geoJsonFile = sys.argv[1]

        convertor = GeoJsonConvertor(geoJsonFile)
        polygons = convertor.getWktPolygons()

        polygonGenerator = FileGenerator()
        polygonGenerator.generatePolygonsFiles(polygons)

        print("End.")


if __name__ == '__main__':
    init()