/*
 * QuPath Project Inspector Script
 * 
 * This script inspects a QuPath project and outputs information about the project
 * and its images as JSON.
 * 
 * Arguments:
 * args[0] - Output file path (optional, outputs to stdout if not provided)
 */

import qupath.lib.projects.ProjectIO
import qupath.lib.projects.Project
import qupath.lib.images.ImageData
import qupath.lib.images.servers.ImageServer
import qupath.lib.projects.ProjectImageEntry
import java.nio.file.Paths
import java.text.SimpleDateFormat
import java.util.Date


// Check we are in a project
def project = getProject()
if (project == null) {
    println("No project found! Did you launch this script with -p?")
    return
}

// Helper function to escape strings for JSON
def escapeJson(String str) {
    if (str == null) return "null"
    return '"' + str.replaceAll('\\\\', '\\\\\\\\')
                   .replaceAll('"', '\\\\"')
                   .replaceAll('\n', '\\\\n')
                   .replaceAll('\r', '\\\\r')
                   .replaceAll('\t', '\\\\t') + '"'
}

// Helper function to format a list as JSON
def formatJsonArray(List list) {
    def items = list.collect { item ->
        if (item instanceof Number) return item.toString()
        if (item instanceof Boolean) return item.toString()
        return escapeJson(item.toString())
    }
    return '[' + items.join(', ') + ']'
}

// Helper function to format a map as JSON
def formatJsonObject(Map map) {
    def items = map.collect { key, value ->
        def jsonKey = escapeJson(key.toString())
        def jsonValue
        if (value instanceof Map) {
            jsonValue = formatJsonObject(value)
        } else if (value instanceof List) {
            if (value.size() > 0 && value[0] instanceof Map) {
                // Array of objects
                def arrayItems = value.collect { item -> formatJsonObject(item) }
                jsonValue = '[' + arrayItems.join(', ') + ']'
            } else {
                jsonValue = formatJsonArray(value)
            }
        } else if (value instanceof Number || value instanceof Boolean) {
            jsonValue = value.toString()
        } else {
            jsonValue = escapeJson(value?.toString())
        }
        return "${jsonKey}: ${jsonValue}"
    }
    return '{' + items.join(', ') + '}'
}

def outputFilePath = args.length > 0 ? args[0] : null

try {
    
    // Prepare the result data structure
    def result = [:]
    
    // Basic project information
    result.uri = project.getURI()
    result.version = project.getVersion() ?: "unknown"
        
    // Process images
    result.images = []
    
    def imageList = project.getImageList()

    if (imageList && !imageList.isEmpty()) {
        for (ProjectImageEntry entry : imageList) {
            def imageInfo = [:]

            imageInfo.id = entry.getID() ?: ""
            imageInfo.entry_path = entry.getEntryPath() ?: ""
            imageInfo.name = entry.getImageName() ?: ""
            imageInfo.description = entry.getDescription() ?: ""
                        

            imageInfo.original_image_name = entry.getOriginalImageName() ?: ""
            imageInfo.unique_name = entry.getUniqueName() ?: ""
            imageInfo.thumbnail_path = entry.getThumbnailPath()?.toString() ?: ""
            imageInfo.server_path = entry.getServerPath()?.toString() ?: ""
            imageInfo.data_path = entry.getImageDataPath()?.toString() ?: ""                        

            def entryUris = entry.getURIs()
            if (entryUris && !entryUris.isEmpty()) {
                imageInfo.uris = entryUris.collect { it.toString() }
            } else {
                imageInfo.uris = []
            }

            try {
                def serverBuilder = entry.getServerBuilder()
                if (imageInfo != null) {
                    imageInfo.server_builder = serverBuilder.toString()
                }
            } catch (Exception e) {
                imageInfo.server_builder = e.getMessage() ?: "Unknown"
            }

            try {
                def imageData = entry.readImageData()
                def server = imageData.getServer()

                imageInfo.server_type = server.getServerType() ?: ""
                imageInfo.num_channels = server.nChannels()
                imageInfo.num_timepoints = server.nTimepoints()
                imageInfo.num_zslices = server.nZSlices()
                imageInfo.height = server.getHeight()
                imageInfo.width = server.getWidth()

                // Get downsample levels
                def downsampleLevels = []
                try {
                    for (int i = 0; i < server.nResolutions(); i++) {
                        downsampleLevels.add(server.getDownsampleForResolution(i))
                    }
                } catch (Exception e) {
                    // If we can't get downsample levels, use a default
                    downsampleLevels = [1.0]
                }
                imageInfo.downsample_levels = downsampleLevels
                                        
                // Get hierarchy information as JSON object
                def hierarchy = [:]
                def hierarchyObj = imageData.getHierarchy()
                if (hierarchyObj != null) {
                    def objects = hierarchyObj.getAllObjects(false)  // false = don't include root object
                    hierarchy.total = objects ? objects.size() : 0
                    
                    // Count different types of objects
                    def detectionObjects = hierarchyObj.getDetectionObjects()
                    def annotationObjects = hierarchyObj.getAnnotationObjects()
                    def rootObject = hierarchyObj.getRootObject()
                    
                    hierarchy.detections = detectionObjects ? detectionObjects.size() : 0
                    hierarchy.annotations = annotationObjects ? annotationObjects.size() : 0
                    hierarchy.has_root_object = rootObject != null
                }
                imageInfo.hierarchy = hierarchy

                
            } catch (Exception e) {
                // If we can't read the image data, set defaults
                imageInfo.server_type = "Unknown"
                imageInfo.num_channels = 0
                imageInfo.num_timepoints = 1
                imageInfo.num_zslices = 1
                imageInfo.height = 0
                imageInfo.width = 0
                imageInfo.downsample_levels = [1.1]
                imageInfo.hierarchy = [total: 0, detections: 0, annotations: 0, has_root_object: false, description: ""]
            }
            
            result.images.add(imageInfo)
        }
    }
    
    // Generate JSON output manually (since JsonBuilder might not be available)
    def jsonOutput = formatJsonObject(result)
    
    // Output to file or stdout
    if (outputFilePath) {
        new File(outputFilePath).text = jsonOutput
    } else {
        println(jsonOutput)
    }
    
} catch (Exception e) {
    System.err.println("Error processing project: " + e.getMessage())
    e.printStackTrace()
    System.exit(1)
}
