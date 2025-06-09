import qupath.lib.io.GsonTools
import qupath.lib.objects.PathObjects
import qupath.lib.regions.ImagePlane
import qupath.lib.roi.ROIs
import qupath.lib.geom.Point2
import qupath.lib.objects.classes.PathClass
import java.awt.Color
import java.io.File

// Parse command line arguments
if (args.length < 2) {
    println("Usage: annotate.groovy <image_name> <geojson_path>")
    println("Arguments provided: " + args.join(", "))
    return
}

def imageName = args[0]
def jsonPath = args[1]

println("Script arguments:")
println("  Image name: " + imageName)
println("  GeoJSON path: " + jsonPath)

// Check we are in a project
def project = getProject()
if (project == null) {
    println("No project found! Did you launch this script with -p?")
    return
}

// Load the image data
println("Looking for image: " + imageName)
def imageEntry = project.getImageList().find { entry ->
    entry.getImageName().contains(imageName)
}
if (imageEntry == null) {
    println("Image not found in project. Available images:")
    project.getImageList().each { entry ->
        println("  - " + entry.getImageName())
    }
    return
}
println("Found image: " + imageEntry.getImageName())
def imageData = imageEntry.readImageData()

// Open the geojson
println("Loading annotations from: " + jsonPath)
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
println("Adding annotations ...")
imageData.getHierarchy().addObjects(newObjects)
println("Added " + newObjects.size() + " annotations from GeoJSON")

// Save image
println("Saving image ...")
imageEntry.saveImageData(imageData)
println("Saved image.")
