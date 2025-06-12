/*
 * QuPath Project Image Addition Script
 * 
 * This script creates a QuPath project (if it doesn't exist) and adds all supported
 * images from the provided paths to the project.
 * 
 * Arguments:
 * args[0] - Project directory path
 * args[1] - JSON file path containing image paths to add
 * args[2] - Output file path for results (number of images added)
 */

import qupath.lib.projects.ProjectIO
import qupath.lib.projects.Project
import qupath.lib.images.ImageData
import qupath.lib.images.servers.ImageServerProvider
import qupath.lib.projects.ProjectImageEntry
import qupath.lib.gui.commands.ProjectCommands
import java.awt.image.BufferedImage
import java.nio.file.Paths
import java.nio.file.Files
import java.io.File
import java.nio.file.Path as JavaPath
import java.net.URI
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

// Parse command line arguments
if (args.length < 3) {
    println("Usage: add.groovy <project_dir> <paths_json_file> <output_file>")
    println("Arguments provided: " + args.join(", "))
    System.exit(1)
}

def projectDir = args[0]
def pathsJsonFile = args[1] 
def outputFile = args[2]

println("Script arguments:")
println("  Project directory: " + projectDir)
println("  Paths JSON file: " + pathsJsonFile)
println("  Output file: " + outputFile)

try {
    // Read the paths from JSON file
    def jsonFile = new File(pathsJsonFile)
    if (!jsonFile.exists()) {
        println("Paths JSON file not found: " + pathsJsonFile)
        System.exit(1)
    }
    
    def gson = new Gson()
    def type = new TypeToken<List<String>>(){}.getType()
    println("paths "+jsonFile.text)

    def imagePaths = gson.fromJson(jsonFile.text, type)
    
    if (imagePaths == null) {
        println("Error: Failed to parse JSON from file. JSON content was: " + jsonFile.text)
        System.exit(1)
    }
    
    println("Number of image paths to process: " + imagePaths.size())
    
    // Ensure project directory exists
    def projectDirPath = Paths.get(projectDir)
    if (!Files.exists(projectDirPath)) {
        Files.createDirectories(projectDirPath)
        println("Created project directory: " + projectDir)
    }
    
    // Define project file path
    def projectFilePath = projectDirPath.resolve("project.qpproj")
    
    // Create or open the project
    Project project
    try {
        if (Files.exists(projectFilePath)) {
            println("Opening existing project: " + projectFilePath)
            project = ProjectIO.loadProject(projectFilePath.toFile(), BufferedImage.class)
        } else {
            println("Creating new project: " + projectDir)
            project = Projects.createProject(new File(projectDir), BufferedImage.class)
            project.syncChanges()
        }
        println("Project opened/created successfully")
    } catch (Exception e) {
        println("Error creating or opening project: " + e.getMessage())
        System.exit(1)
    }
    
    // Define supported file extensions (matching WSI_SUPPORTED_FILE_EXTENSIONS from Python)
    def supportedExtensions = [
        ".dcm", ".svs", ".tif", ".tiff"
    ] as Set
    
    // Helper function to check if file is supported
    def isSupportedImage = { File file ->
        if (!file.isFile()) return false
        def extension = ""
        def name = file.getName().toLowerCase()
        def lastDot = name.lastIndexOf('.')
        if (lastDot > 0) {
            extension = name.substring(lastDot)
        }
        return supportedExtensions.contains(extension)
    }
    
    // Collect all image files to process
    def filesToProcess = []
    
    for (String pathStr : imagePaths) {
        def path = new File(pathStr)
        if (path.isDirectory()) {
            // Recursively find all supported images in directory
            path.eachFileRecurse { file ->
                if (isSupportedImage(file)) {
                    filesToProcess.add(file)
                }
            }
        } else if (isSupportedImage(path)) {
            filesToProcess.add(path)
        }
    }
    
    println("Found " + filesToProcess.size() + " supported image files to add")
    
    // Add images to project
    // See https://forum.image.sc/t/creating-project-from-command-line/45608/2
    def addedCount = 0
    def errors = []
    
    for (File imageFile : filesToProcess) {
        try {
            def imagePath = imageFile.getAbsolutePath()
            println("Adding image: " + imagePath)
            
            // Create URI for the image
            def imageUri = imageFile.toURI()
            println("Image URI: " + imageUri)

            // Check if image is already in project
            def existingEntry = project.getImageList().find { entry ->
                def entryUris = entry.getURIs()
                return entryUris.any { uri -> uri.equals(imageUri) }
            }
            
            if (existingEntry != null) {
                println("Image already exists in project: " + imageFile.getName())
                continue
            }
            println("Image not found in project, proceeding to add...")
            
            // Try to create image server to validate the image
            def serverBuilder = ImageServerProvider.getPreferredUriImageSupport(BufferedImage.class, imageUri.toString())
            if (serverBuilder == null) {
                errors.add("No image server builder found for: " + imageFile.getAbsolutePath())
                continue
            }
            println("Image server builder found for: " + imageFile.getName())

            def builder = serverBuilder.builders.get(0)
            // Make sure we don't have null 
            if (builder == null) {
                println("Image not supported: " + imagePath)
                continue
            }
            println("Image server builder created for: " + imageFile.getName())
            
            // Add image to project
            println("Calling addImage... ")
            def addImageStart = System.currentTimeMillis()
            def entry = project.addImage(builder)
            def addImageDuration = (System.currentTimeMillis() - addImageStart) / 1000.0
            println("addImage took ${addImageDuration} seconds")

            println("Calling setImageName... "+imageFile.getName())
            def setImageNameStart = System.currentTimeMillis()
            entry.setImageName(imageFile.getName())
            def setImageNameDuration = (System.currentTimeMillis() - setImageNameStart) / 1000.0
            println("setImageName took ${setImageNameDuration} seconds")

            // Set a particular image type
            println("Calling readImageData... ")
            def readImageDataStart = System.currentTimeMillis()
            def imageData = entry.readImageData()
            def readImageDataDuration = (System.currentTimeMillis() - readImageDataStart) / 1000.0
            println("readImageData took ${readImageDataDuration} seconds")

            println("Calling setImageType... ")
            def setImageTypeStart = System.currentTimeMillis()
            imageData.setImageType(ImageData.ImageType.BRIGHTFIELD_H_DAB)
            def setImageTypeDuration = (System.currentTimeMillis() - setImageTypeStart) / 1000.0
            println("setImageType took ${setImageTypeDuration} seconds")

            println("Calling saveImageData... ")
            def saveImageDataStart = System.currentTimeMillis()
            entry.saveImageData(imageData)
            def saveImageDataDuration = (System.currentTimeMillis() - saveImageDataStart) / 1000.0
            println("saveImageData took ${saveImageDataDuration} seconds")

            // Write a thumbnail if we can
            println("Calling getThumbnailRGB... ")
            var img = ProjectCommands.getThumbnailRGB(imageData.getServer());
            def setThumbnailStart = System.currentTimeMillis()
            entry.setThumbnail(img)
            def setThumbnailDuration = (System.currentTimeMillis() - setThumbnailStart) / 1000.0
            println("setThumbnail took ${setThumbnailDuration} seconds")
            
            addedCount++
            println("Adding image completed for image " + addedCount + ", " + imageFile.getName())
            
        } catch (Exception e) {
            def errorMsg = "Error adding image '" + imageFile.getAbsolutePath() + "': " + e.getMessage()
            errors.add(errorMsg)
            println("ERROR: " + errorMsg)
        }
    }
    
    // Save the project
    try {
        project.syncChanges()
        println("Project saved successfully")
    } catch (Exception e) {
        println("Warning: Error saving project: " + e.getMessage())
    }
    
    // Output results
    def result = [
        added_count: addedCount,
        total_files_processed: filesToProcess.size(),
        errors: errors
    ]
    
    def resultJson = gson.toJson(result)
    new File(outputFile).text = resultJson
    
    println("Results written to: " + outputFile)
    println("Successfully added " + addedCount + " images out of " + filesToProcess.size() + " files processed")
    
    if (errors.size() > 0) {
        println("Errors encountered:")
        errors.each { error -> println("  - " + error) }
    }
    
} catch (Exception e) {
    System.err.println("Error in add script: " + e.getMessage())
    e.printStackTrace()
    System.exit(1)
}
