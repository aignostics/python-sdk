import qupath.lib.io.GsonTools
import qupath.lib.objects.PathObjects
import qupath.lib.regions.ImagePlane
import qupath.lib.roi.ROIs
import qupath.lib.geom.Point2
import qupath.lib.objects.classes.PathClass
import java.awt.Color
import java.io.File

def jsonPath = "/Users/helmut/Library/Application Support/aignostics/results/28b5b479-46da-4ee5-990e-ab0e200c7a40/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627/cell_classification_geojson_polygons.json"

// Check if file exists
def jsonFile = new File(jsonPath)
if (!jsonFile.exists()) {
    println("File not found: " + jsonPath)
    return
}

def gson = GsonTools.getInstance(true)
def json = jsonFile.text

// Parse as GeoJSON
def type = new com.google.gson.reflect.TypeToken<Map<String, Object>>(){}.getType()
def geoJsonData = gson.fromJson(json, type)

// Get current image plane
def imageData = getCurrentImageData()
def plane = ImagePlane.getDefaultPlane()

// Create list for new objects
def newObjects = []

// Process GeoJSON features
def features = geoJsonData.features
features.each { feature ->
    def geometry = feature.geometry
    def properties = feature.properties ?: [:]
    
    if (geometry.type == "Polygon") {
        // Get exterior ring coordinates and convert to Point2 objects
        def coordinates = geometry.coordinates[0]
        def points = coordinates.collect { coord ->
            return new Point2(coord[0] as double, coord[1] as double)
        }
        
        // Create polygon ROI
        def roi = ROIs.createPolygonROI(points, plane)
        
        // Create annotation object instead of detection
        def pathObject = PathObjects.createAnnotationObject(roi)
        
        // Set classification if available
        if (properties.classification) {
            def className = properties.classification.name
            def colorArray = properties.classification.color
            
            // Create PathClass with color
            def pathClass = PathClass.fromString(className)
            if (colorArray && colorArray.size() >= 3) {
                def color = new Color(colorArray[0] as int, colorArray[1] as int, colorArray[2] as int)
                pathClass = PathClass.fromString(className, color.getRGB())
            }
            pathObject.setPathClass(pathClass)
        }
        
        // Add other properties as metadata
        properties.each { key, value ->
            if (key != "classification") {
                pathObject.getMetadata().put(key.toString(), value.toString())
            }
        }
        
        newObjects.add(pathObject)
    }
}

// Add objects to hierarchy
addObjects(newObjects)
println("Added " + newObjects.size() + " annotations from GeoJSON")