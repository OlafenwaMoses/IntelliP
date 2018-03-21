"""
(c) Moses and Joh Olafenwa 2018
Website : https://moses.specpal.science , https://john.specpal.science
---------------------------

This is the file that contains all the python code
for the IntelliP.

"""

#Below is the imports needed for the program
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.app import runTouchApp
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.clock import mainthread
from kivy.config import Config
import os
from imageai.Prediction import ImagePrediction
import threading
import json

# Below we obtain the working directory of our python program fro use later in the program.
execution_path = os.getcwd()

# This value is created to enable us to track loaded pages in each gallery category
global gallerySteps
gallerySteps = 1

# Below is an aray of all the folders in the computer we intend to sacn for photos
folders_array = []
pictures_folder = os.environ["USERPROFILE"] + "\\Pictures\\"
folders_array.append(pictures_folder)
download_folder = os.environ["USERPROFILE"] + "\\Downloads\\"
folders_array.append(download_folder)
documents_folder = os.environ["USERPROFILE"] + "\\Documents\\"
folders_array.append(documents_folder)
videos_folder = os.environ["USERPROFILE"] + "\\Videos\\"
folders_array.append(videos_folder)
desktop_folder = os.environ["USERPROFILE"] + "\\Desktop\\"
folders_array.append(desktop_folder)


# Below is a dictionary of arrays of photos extracted and categorized by our image prediction object
pictures_array = []
pictures_object_array = []

pictures_dictionary = {}
pictures_animals_array = []
pictures_dictionary["animals"] = pictures_animals_array
pictures_seaanimals_array = []
pictures_dictionary["seaanimals"] = pictures_seaanimals_array
pictures_birds_array = []
pictures_dictionary["birds"] = pictures_birds_array
pictures_objects_array = []
pictures_dictionary["objects"] = pictures_objects_array
pictures_electronics_array = []
pictures_dictionary["electronics"] = pictures_electronics_array
pictures_dresses_array = []
pictures_dictionary["dresses"] = pictures_dresses_array
pictures_foods_array = []
pictures_dictionary["foods"] = pictures_foods_array
pictures_plants_array = []
pictures_dictionary["plants"] = pictures_plants_array
pictures_aircrafts_array = []
pictures_dictionary["aircrafts"] = pictures_aircrafts_array
pictures_places_array = []
pictures_dictionary["places"] = pictures_places_array
pictures_vehicles_array = []
pictures_dictionary["vehicles"] = pictures_vehicles_array
pictures_people_array = []
pictures_dictionary["people"] = pictures_people_array

# Below is our image prediction object
imagePrediction = ImagePrediction()
imagePrediction.setModelTypeAsResNet()
imagePrediction.setModelPath(execution_path + "\\resnet50_weights_tf_dim_ordering_tf_kernels.h5")
imagePrediction.setJsonPath(execution_path + "\\imagenet_class_index.json")




# Below is our main application layout
mainLayout = FloatLayout()
mainLayout.size_hint = (1, None)
mainLayout.size = (Window.width, Window.height)



# Below is our layout when we are  scanning the computer for photos. It also shows the progress.
scanLayout = GridLayout()
scanLayout.cols = 1
scanLayout.size_hint = (1, None)
scanLayout.size = (Window.width, Window.height)
with scanLayout.canvas.before:
    Color(0,1,0,1)
    scanLayout.rect = Rectangle(size= Window.size, pos = scanLayout.pos)

label1 = Label()
label1.size_hint_x = 1
label1.font_size = 15
label1.text = "IntelliP is scanning your pictures.\n" \
              "It will perform this operation once.\n" \
              "Once done, it won't need to scan again\n" \
              "It will load your pictures in intelligent\n" \
              "categories."
scanLayout.add_widget(label1)

label2 = Label()
label2.size_hint_x = 1
label2.font_size = 20
label2.text = "Pictures found : "
scanLayout.add_widget(label2)


scanLoader = AsyncImage()
try:
    scanLoader.source = execution_path + "\\loading.gif"
    scanLoader.size_hint = (3, None)
    scanLoader.height = 300
    scanLayout.add_widget(scanLoader)
except:
    print("Skipped")



# Below is the class of the Button than displays the "About" information of the Application
class AboutButton(Button):
    def __init__(self, **kwargs):
        super(AboutButton, self).__init__(**kwargs)

    def on_press(self):
        aboutLayout = GridLayout()
        aboutLayout.cols = 1
        aboutLayout.size_hint = (1, None)
        aboutLayout.size = (Window.width, Window.height)
        with aboutLayout.canvas.before:
            Color(0, 1, 0, 1)
            aboutLayout.rect = Rectangle(size=Window.size, pos=aboutLayout.pos)

        aboutText1 = Label()
        aboutText1.font_size = 30
        aboutText1.text = "IntelliP"

        aboutText2 = Label()
        aboutText2.font_size = 20
        aboutText2.text = "(Intelligent Photos)"

        aboutText3 = Label()
        aboutText3.font_size = 15
        aboutText3.text = "IntelliP is an intelligent photo \n" \
                          "Application that organizes your \n" \
                          "system photos into 12 distinct \n" \
                          "categories using AI. This Application \n" \
                          "serves as a demo App for the ImageAI \n" \
                          "library by Moses & John Olafenwa."

        aboutText4 = Label()
        aboutText4.font_size = 20
        aboutText4.text = "(c) Moses & John Olafenwa, 2018."

        closeAbout = CloseAbout(aboutLayout)
        closeAbout.text = "Back"
        closeAbout.font_size = 20
        closeAbout.size_hint = (1, None)
        closeAbout.height = 50

        aboutLayout.add_widget(aboutText1)
        aboutLayout.add_widget(aboutText2)
        aboutLayout.add_widget(aboutText3)
        aboutLayout.add_widget(aboutText4)
        aboutLayout.add_widget(closeAbout)

        mainLayout.add_widget(aboutLayout)



# Below is the class of the button that closes the "About" application layout when clicked
class CloseAbout(Button):
    def __init__(self, aboutLayout, **kwargs):
        super(CloseAbout, self).__init__(**kwargs)
        self.about_layout = aboutLayout

    def on_press(self):
        mainLayout.remove_widget(self.about_layout)



# Below is the class of the layout used to display each page of at most 10 pictures in each photo category
class Scroller(ScrollView,):
    def __init__(self, actionLayout, **kwargs):
        super(Scroller, self).__init__(**kwargs)
        self.size_hint = (1, None)
        self.size = (Window.width, Window.height)
        self.scroll_type = ["bars", "content"]
        self.action_layout = actionLayout

    def on_scroll_stop(self, touch, check_children=True):
        threshold = self.vbar[0] * 100
        if(int(threshold) < 5):
            response = loadNext()
            if response:
                mainLayout.remove_widget(self)
                mainLayout.remove_widget(self.action_layout)

        elif(int(threshold) == 70):
            response = loadPrevious()
            if response:
                mainLayout.remove_widget(self)
                mainLayout.remove_widget(self.action_layout)

        super(Scroller, self).on_scroll_stop(touch)






# Below is the layout that shows all the photo categories
galleryScroll = ScrollView()
galleryScroll.size_hint = (1, None)
galleryScroll.size = (Window.width, Window.height)
galleryScroll.scroll_type = ["bars", "content"]

galleryScroll.bar_width = 20
galleryScroll.bar_inactive_color = [0.3, 0.9, 0,5, 0.9]
with galleryScroll.canvas.before:
    Color(0,1,0,1)
    galleryScroll.rect = Rectangle(size= Window.size, pos = galleryScroll.pos)

galleryGrid = GridLayout(cols=2, spacing=10, size_hint_y=None)
galleryGrid.cols = 2
galleryGrid.bind(minimum_height = galleryGrid.setter('height'))







# Below is the Thread that scans the computer for photos, run image prediction on them and store them in
# "pictures.json" file and "pictures_monitor.json" file.
class ScanThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    # Below function is used to update the scan layout on the progress of the comuter scanning and image predictions
    @mainthread
    def updateUI(self, message):
        label2.text = message
    # The function below is used after the predictions are complete to show the photo gallery layout
    @mainthread
    def finalUpdateUI(self, value):
        label2.text = "Total Pictures found : " + str(value)

        # The code below writes the photo categories dictionary to a json file for use later
        with open(execution_path + "\\pictures.json", "w+") as outfile:
            json.dump(pictures_dictionary, outfile, indent=4, sort_keys=True, separators=(",", " : "), ensure_ascii=True)
            outfile.close()

        # The code below make checks and show the photo categories with pictures in them
        if(len(pictures_animals_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_animals_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                print("Skipped")

            categoryLabel = Label()
            categoryLabel.text = " >>> Animals"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Animals", pictures_animals_array)
            loadButton.text = "View Animals"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_seaanimals_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_seaanimals_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                print("Skipped")

            categoryLabel = Label()
            categoryLabel.text = " >>> Sea Animals"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Sea Animals", pictures_seaanimals_array)
            loadButton.text = "View Sea Animals"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_birds_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_birds_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                print("Skipped")

            categoryLabel = Label()
            categoryLabel.text = " >>> Birds"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Birds", pictures_birds_array)
            loadButton.text = "View Birds"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_objects_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_objects_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                print ("Skipped")

            categoryLabel = Label()
            categoryLabel.text = " >>> Objects"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Objects", pictures_objects_array)
            loadButton.text = "View Objects"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_electronics_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_electronics_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                print("Skipped")

            categoryLabel = Label()
            categoryLabel.text = " >>> Electronics"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Electronics", pictures_electronics_array)
            loadButton.text = "View Electronics"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_dresses_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_dresses_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                print("Skipped")

            categoryLabel = Label()
            categoryLabel.text = " >>> Dresses"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Dresses", pictures_dresses_array)
            loadButton.text = "View Dresses"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_foods_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_foods_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                print("Skipped")

            categoryLabel = Label()
            categoryLabel.text = " >>> Foods"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Foods", pictures_foods_array)
            loadButton.text = "View Foods"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_plants_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_plants_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                print("Skipped")

            categoryLabel = Label()
            categoryLabel.text = " >>> Plants"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Plants", pictures_plants_array)
            loadButton.text = "Plants"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_aircrafts_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_aircrafts_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                print("Skipped")

            categoryLabel = Label()
            categoryLabel.text = " >>> Aircrafts"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Aircrafts", pictures_aircrafts_array)
            loadButton.text = "View Aircrafts"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_places_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_places_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Places"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Places", pictures_places_array)
            loadButton.text = "View Places"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_vehicles_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_vehicles_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Vehicles"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Vehicles", pictures_vehicles_array)
            loadButton.text = "View Vehicles"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_people_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_people_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> People"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> People", pictures_people_array)
            loadButton.text = "View People"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)


        # Below is the code for extra button actions and dummy labels for interface optimization

        dummyGridObject = Label()
        dummyGridObject.size_hint_y = None
        dummyGridObject.height = "100"
        dummyGridObject.text = "  . \n" \
                               "  .  \n" \
                               "  .  \n"
        galleryGrid.add_widget(dummyGridObject)

        detailsGrid = GridLayout()
        detailsGrid.cols = 3
        detailsGrid.size_hint = (1, None)

        dummy1 = Label()
        dummy1.size_hint = (1, None)
        detailsGrid.add_widget(dummy1)

        aboutbutton = AboutButton()
        aboutbutton.text = "About"
        aboutbutton.font_size = 15
        aboutbutton.size_hint = (2, None)
        aboutbutton.height = 30
        detailsGrid.add_widget(aboutbutton)

        dummy2 = Label()
        dummy2.size_hint = (1, None)
        detailsGrid.add_widget(dummy2)

        mainLayout.remove_widget(scanLayout)
        galleryScroll.add_widget(galleryGrid)

        mainLayout.add_widget(galleryScroll)
        mainLayout.add_widget(detailsGrid)



    # This is the function that starts the thread and initate the image scanning and image prediction process
    def run(self):
        count = 0

        # The Code below obtains the pictures from each folder in the folders_array and add it to the "pictures_array"
        for eachFolder in folders_array:

            if eachFolder ==  os.environ["USERPROFILE"] + "\\Pictures\\":
                for top_dir, sub_dir_array, files_array in os.walk(eachFolder, topdown=True, followlinks=True):

                    for file in files_array:
                        if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".gif") or file.endswith(
                                ".PNG") or file.endswith(".JPG") or file.endswith(".GIF"):
                            count += 1

                            if ((count % 10) == 0):
                                self.updateUI("Pictures found : " + str(count))


                            pictures_array.append(os.path.join(top_dir, file))
            else:
                files = os.listdir(eachFolder)
                for file in files:
                    if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".gif") or file.endswith(
                            ".PNG") or file.endswith(".JPG") or file.endswith(".GIF"):
                        count += 1

                        if ((count % 10) == 0):
                            self.updateUI("Pictures found : " + str(count))


                        pictures_array.append(eachFolder + file)


        counter = 0

        self.updateUI("Loading Intelligence Module....")
        imagePrediction.loadModel()
        self.updateUI("Intelligence Module loaded....")

        # The code below obtains our manually edited " gallery_class.json " in preparation for photo
        # categorization after image prediction
        with open(execution_path + "\\gallery_class.json") as inputFile:
            gallery_class = json.load(inputFile)

        # The code below performs image prediction for all images in the " pictures_array "
        for eachFile in pictures_array:
            counter += 1
            try:
                predictions, percentage_probabilities = imagePrediction.predictImage(eachFile,
                                                                                     result_count=1)
                # The code below creates a special Image Object for after each image prediction
                # and adds it to the corresponding picture category array

                for index in range(len(predictions)):
                    print(predictions[index])
                    imageDictionary = {}
                    imageDictionary["path"] = str(eachFile)
                    imageDictionary["prediction"] = predictions[index]

                    imageCategory = gallery_class[predictions[index]]
                    imageDictionary["category"] = imageCategory
                if (imageCategory == "animals"):
                    pictures_animals_array.append(imageDictionary)
                elif (imageCategory == "sea animals"):
                    pictures_seaanimals_array.append(imageDictionary)
                elif (imageCategory == "birds"):
                    pictures_birds_array.append(imageDictionary)
                elif (imageCategory == "objects"):
                    pictures_objects_array.append(imageDictionary)
                elif (imageCategory == "electronics"):
                    pictures_electronics_array.append(imageDictionary)
                elif (imageCategory == "dresses"):
                    pictures_dresses_array.append(imageDictionary)
                elif (imageCategory == "foods"):
                    pictures_foods_array.append(imageDictionary)
                elif (imageCategory == "plants"):
                    pictures_plants_array.append(imageDictionary)
                elif (imageCategory == "aircrafts"):
                    pictures_aircrafts_array.append(imageDictionary)
                elif (imageCategory == "places"):
                    pictures_places_array.append(imageDictionary)
                elif (imageCategory == "vehicles"):
                    pictures_vehicles_array.append(imageDictionary)
                elif (imageCategory == "people"):
                    pictures_people_array.append(imageDictionary)
            except:
                continue

            self.updateUI("Processing " + str(counter) + " of " + str(len(pictures_array)) + " pictures")
        # The code below creates " pictures_monitor.json " file that is used to keep track of processed photos
        # during a computer rescan.
        pictures_monitor_dictionary = {}
        for eachItem in pictures_array:
            newItem = eachItem
            pictures_monitor_dictionary[str(newItem)] = ""

        with open(execution_path + "\\pictures_monitor.json", "w+") as monitorfile:
            json.dump(pictures_monitor_dictionary, monitorfile, indent=4, sort_keys=True, separators=(",", " : "), ensure_ascii=True)
            monitorfile.close()


        self.finalUpdateUI(len(pictures_array))



# The class below performs a computer rescan and image prediction to add new photos to its list. It does
# so and updates the "pictures.json" file and "pictures_json.json" file accordingly.
class ReScanThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)


    @mainthread
    def updateUI(self, message):
        label2.text = message


    @mainthread
    def updateFinalUI(self):
        with open(execution_path + "\\pictures.json") as inputFile:
            json_data = json.load(inputFile)

            rescangalleryScroll = ScrollView()
            rescangalleryScroll.size_hint = (1, None)
            rescangalleryScroll.size = (Window.width, Window.height)
            rescangalleryScroll.scroll_type = ["bars", "content"]

            rescangalleryScroll.bar_width = 20
            rescangalleryScroll.bar_inactive_color = [0.3, 0.9, 0, 5, 0.9]
            with galleryScroll.canvas.before:
                Color(0, 1, 0, 1)
                rescangalleryScroll.rect = Rectangle(size=Window.size, pos=rescangalleryScroll.pos)

            rescangalleryGrid = GridLayout(cols=2, spacing=10, size_hint_y=None)
            rescangalleryGrid.cols = 2
            rescangalleryGrid.bind(minimum_height=rescangalleryGrid.setter('height'))

            animals_data = json_data["animals"]
            for eachObject in animals_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "animals"
                pictures_animals_array.append(imageDictionary)

            seaanimals_data = json_data["seaanimals"]
            for eachObject in seaanimals_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "seaanimals"
                pictures_seaanimals_array.append(imageDictionary)

            birds_data = json_data["birds"]
            for eachObject in birds_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "birds"
                pictures_birds_array.append(imageDictionary)

            objects_data = json_data["objects"]
            for eachObject in objects_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "objects"
                pictures_objects_array.append(imageDictionary)

            electronics_data = json_data["electronics"]
            for eachObject in electronics_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "electronics"
                pictures_electronics_array.append(imageDictionary)

            dresses_data = json_data["dresses"]
            for eachObject in dresses_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "dresses"
                pictures_dresses_array.append(imageDictionary)

            foods_data = json_data["foods"]
            for eachObject in foods_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "foods"
                pictures_foods_array.append(imageDictionary)

            plants_data = json_data["plants"]
            for eachObject in plants_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "plants"
                pictures_plants_array.append(imageDictionary)

            aircrafts_data = json_data["aircrafts"]
            for eachObject in aircrafts_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "aircrafts"
                pictures_aircrafts_array.append(imageDictionary)

            places_data = json_data["places"]
            for eachObject in places_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "places"
                pictures_places_array.append(imageDictionary)

            vehicles_data = json_data["vehicles"]
            for eachObject in vehicles_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "vehicles"
                pictures_vehicles_array.append(imageDictionary)

            people_data = json_data["people"]
            for eachObject in people_data:
                imageDictionary = {}
                imageDictionary["path"] = eachObject["path"]
                imageDictionary["prediction"] = eachObject["prediction"]
                imageDictionary["category"] = "people"
                pictures_people_array.append(imageDictionary)

            if (len(pictures_animals_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_animals_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> Animals"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> Animals", pictures_animals_array)
                loadButton.text = "View Animals"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)

            if (len(pictures_seaanimals_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_seaanimals_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> Sea Animals"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> Sea Animals", pictures_seaanimals_array)
                loadButton.text = "View Sea Animals"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)

            ## Adding the Categories to UI

            if (len(pictures_birds_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_birds_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> Birds"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> Birds", pictures_birds_array)
                loadButton.text = "View Birds"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)

            if (len(pictures_objects_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_objects_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> Objects"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> Objects", pictures_objects_array)
                loadButton.text = "View Objects"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)

            if (len(pictures_electronics_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_electronics_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> Electronics"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> Electronics", pictures_electronics_array)
                loadButton.text = "View Electronics"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)

            if (len(pictures_dresses_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_dresses_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> Dresses"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> Dresses", pictures_dresses_array)
                loadButton.text = "View Dresses"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)

            if (len(pictures_foods_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_foods_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> Foods"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> Foods", pictures_foods_array)
                loadButton.text = "View Foods"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)

            if (len(pictures_plants_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_plants_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> Plants"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> Plants", pictures_plants_array)
                loadButton.text = "Plants"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)

            if (len(pictures_aircrafts_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_aircrafts_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> Aircrafts"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> Aircrafts", pictures_aircrafts_array)
                loadButton.text = "View Aircrafts"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)

            if (len(pictures_places_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_places_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> Places"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> Places", pictures_places_array)
                loadButton.text = "View Places"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)

            if (len(pictures_vehicles_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_vehicles_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> Vehicles"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> Vehicles", pictures_vehicles_array)
                loadButton.text = "View Vehicles"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)

            if (len(pictures_people_array) > 0):
                categoryGrid = GridLayout(size_hint_y=None, height=400)
                categoryGrid.cols = 1

                categoryImage = AsyncImage(size_hint_y=None, height=300)
                try:
                    categoryImage.source = pictures_people_array[0]["path"]
                    categoryGrid.add_widget(categoryImage)
                except:
                    None

                categoryLabel = Label()
                categoryLabel.text = " >>> People"
                categoryLabel.font_size = 15
                categoryGrid.add_widget(categoryLabel)

                loadButton = LoadGalleryButton(" >> People", pictures_people_array)
                loadButton.text = "View People"
                loadButton.font_size = 15
                categoryGrid.add_widget(loadButton)

                rescangalleryGrid.add_widget(categoryGrid)


            dummyGridObject = Label()
            dummyGridObject.size_hint_y = None
            dummyGridObject.height = "100"
            dummyGridObject.text = "  . \n" \
                                   "  .  \n" \
                                   "  .  \n"
            rescangalleryGrid.add_widget(dummyGridObject)

            rescangalleryScroll.add_widget(rescangalleryGrid)
            mainLayout.add_widget(galleryScroll)

            detailsGrid = GridLayout()
            detailsGrid.cols = 3
            detailsGrid.size_hint = (1, None)

            dummy1 = Label()
            dummy1.size_hint = (1, None)
            detailsGrid.add_widget(dummy1)

            aboutbutton = AboutButton()
            aboutbutton.text = "About"
            aboutbutton.font_size = 15
            aboutbutton.size_hint = (2, None)
            aboutbutton.height = 30
            detailsGrid.add_widget(aboutbutton)

            dummy2 = Label()
            dummy2.size_hint = (1, None)
            detailsGrid.add_widget(dummy2)

            mainLayout.remove_widget(scanLayout)
            mainLayout.add_widget(detailsGrid)

    def run(self):
        all_pictures_array = []
        found_pictures_array = []



        with open(execution_path + "\\pictures.json", "r") as picturesFile:
            pictures_class = json.load(picturesFile)
            picturesFile.close()

        rescanpictures_animals_array = pictures_class["animals"]
        rescanpictures_seaanimals_array = pictures_class["seaanimals"]
        rescanpictures_birds_array = pictures_class["birds"]
        rescanpictures_objects_array = pictures_class["objects"]
        rescanpictures_electronics_array = pictures_class["electronics"]
        rescanpictures_dresses_array = pictures_class["dresses"]
        rescanpictures_foods_array = pictures_class["foods"]
        rescanpictures_plants_array = pictures_class["plants"]
        rescanpictures_aircrafts_array = pictures_class["aircrafts"]
        rescanpictures_places_array = pictures_class["places"]
        rescanpictures_vehicles_array = pictures_class["vehicles"]
        rescanpictures_people_array = pictures_class["people"]

        count = 0

        for eachFolder in folders_array:

            if eachFolder == os.environ["USERPROFILE"] + "\\Pictures\\" :
                for top_dir, sub_dir_array, files_array in os.walk(eachFolder, topdown=True, followlinks=True):

                    for file in files_array:
                        if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".gif") or file.endswith(
                                ".PNG") or file.endswith(".JPG") or file.endswith(".GIF"):
                            count += 1

                            all_pictures_array.append(os.path.join(top_dir, file))
            else:
                files = os.listdir(eachFolder)
                for file in files:
                    if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".gif") or file.endswith(
                            ".PNG") or file.endswith(".JPG") or file.endswith(".GIF"):
                        count += 1

                        all_pictures_array.append(eachFolder + file)

        # Prediction Object
        rescanimagePrediction = ImagePrediction()
        rescanimagePrediction.setModelTypeAsResNet()
        rescanimagePrediction.setModelPath(execution_path + "\\resnet50_weights_tf_dim_ordering_tf_kernels.h5")
        rescanimagePrediction.setJsonPath(execution_path + "\\imagenet_class_index.json")


        with open(execution_path + "\\gallery_class.json") as inputFile:
            gallery_class = json.load(inputFile)
            inputFile.close()

        count = 0

        with open(execution_path + "\\pictures_monitor.json") as monitorFile:
            allpictures = json.load(monitorFile)
            monitorFile.close()
            for eachImage in all_pictures_array:
                try:
                    string = allpictures[str(eachImage)]
                except:
                    found_pictures_array.append(eachImage)
        count = 0
        if len(found_pictures_array) > 0 :
            self.updateUI("Loading Intelligence Model...")
            rescanimagePrediction.loadModel()
            for eachImage in found_pictures_array:
                try:
                    count += 1
                    self.updateUI("Processing " + str(count) + " of " + str(len(found_pictures_array)))
                    predictions, percentage_probabilities = rescanimagePrediction.predictImage(eachImage,
                                                                                         result_count=1)
                    for index in range(len(predictions)):
                        imageDictionary = {}
                        imageDictionary["path"] = str(eachImage)
                        imageDictionary["prediction"] = predictions[index]

                        imageCategory = gallery_class[predictions[index]]
                        imageDictionary["category"] = imageCategory

                        if (imageCategory == "animals"):
                            rescanpictures_animals_array.append(imageDictionary)
                        elif (imageCategory == "sea animals"):
                            rescanpictures_seaanimals_array.append(imageDictionary)
                        elif (imageCategory == "birds"):
                            rescanpictures_birds_array.append(imageDictionary)
                        elif (imageCategory == "objects"):
                            rescanpictures_objects_array.append(imageDictionary)
                        elif (imageCategory == "electronics"):
                            rescanpictures_electronics_array.append(imageDictionary)
                        elif (imageCategory == "dresses"):
                            rescanpictures_dresses_array.append(imageDictionary)
                        elif (imageCategory == "foods"):
                            rescanpictures_foods_array.append(imageDictionary)
                        elif (imageCategory == "plants"):
                            rescanpictures_plants_array.append(imageDictionary)
                        elif (imageCategory == "aircrafts"):
                            rescanpictures_aircrafts_array.append(imageDictionary)
                        elif (imageCategory == "places"):
                            rescanpictures_places_array.append(imageDictionary)
                        elif (imageCategory == "vehicles"):
                            rescanpictures_vehicles_array.append(imageDictionary)
                        elif (imageCategory == "people"):
                            rescanpictures_people_array.append(imageDictionary)
                except:
                    continue


        for eachPath in found_pictures_array:
            allpictures[eachPath] = ""


        if count > 0:
            self.updateUI("Getting things Ready...")
            with open(execution_path + "\\pictures.json", "w+") as picturesFile:
                json.dump(pictures_class, picturesFile, indent=4, sort_keys=True, separators=(",", " : "),
                          ensure_ascii=True)
                picturesFile.close()

            with open(execution_path + "\\pictures_monitor.json", "w+") as monitorFile:
                json.dump(allpictures, monitorFile, indent=4, sort_keys=True, separators=(",", " : "),
                          ensure_ascii=True)
                monitorFile.close()

            pictures_animals_array.clear()
            pictures_seaanimals_array.clear()
            pictures_birds_array.clear()
            pictures_objects_array.clear()
            pictures_electronics_array.clear()
            pictures_dresses_array.clear()
            pictures_foods_array.clear()
            pictures_plants_array.clear()
            pictures_aircrafts_array.clear()
            pictures_places_array.clear()
            pictures_vehicles_array.clear()
            pictures_people_array.clear()

            self.updateFinalUI()
        else:
            self.updateFinalUI()


        






# The below class is the code for button that initiates the computer scanning process
class ScanButton(Button):
    def __init__(self, **kwargs):
        super(ScanButton, self).__init__(**kwargs)

    def on_press(self):
        scanning = ScanThread()
        scanning.start()
        mainLayout.add_widget(scanLayout)

# The below class is the code for button that initiates the computer rescanning process
class ReScanButton(Button):
    def __init__(self, galleryLayout, detailsLayout, **kwargs):
        super(ReScanButton, self).__init__(**kwargs)
        self.gallery_layout = galleryLayout
        self.details_layout = detailsLayout

    def on_press(self):
        rescanning = ReScanThread()
        rescanning.start()
        label1.text = "Re-scanning of system photos is \n" \
                      "ongoing. Wait while it completes"
        mainLayout.remove_widget(self.gallery_layout)
        mainLayout.remove_widget(self.details_layout)
        mainLayout.add_widget(scanLayout)

# The below class is the code for button that initiates the "loadGallery()" function for aeach photo category
class LoadGalleryButton(Button):
    def __init__(self, category_name, category_array, **kwargs):
        super(LoadGalleryButton, self).__init__(**kwargs)
        self.category_name = category_name
        self.category_array = category_array

    def on_press(self):
        loadGallery(self.category_name, self.category_array)

 # The below class is the code for button that removes the loaded photo category
class CloseGallery(Button):
    def __init__(self, gallery_layout, gallery_action, **kwargs):
        super(CloseGallery, self).__init__(**kwargs)
        self.gallery_layout = gallery_layout
        self.gallery_action = gallery_action

    def on_press(self):
        mainLayout.remove_widget(self.gallery_layout)
        mainLayout.remove_widget(self.gallery_action)

 # The below class is the code for button that shows an image in full view
class ViewImage(Button):
    def __init__(self, imagePath, imageLabel, **kwargs):
        super(ViewImage, self).__init__(**kwargs)
        self.image_path = imagePath
        self.image_label = imageLabel

    def on_press(self):
        imageLayout = GridLayout()
        imageLayout.size_hint = (1, None)
        imageLayout.size = (Window.width, Window.height)
        imageLayout.cols = 1
        with imageLayout.canvas.before:
            Color(0, 1, 0, 1)
            imageLayout.rect = Rectangle(size=Window.size, pos=imageLayout.pos)

        imageView = AsyncImage(size_hint_y = 6, size_hint_x = 1)
        try:
            imageView.source = self.image_path
            imageLayout.add_widget(imageView)
        except:
            None

        imageLabel = Label(size_hint_y = 1)
        imageLabel.text = self.image_label
        imageLabel.font_size = 20
        imageLayout.add_widget(imageLabel)

        closeImage = CloseImage(imageLayout)
        closeImage.text = " << Back "
        closeImage.size_hint_y = 1
        closeImage.font_size = 20
        imageLayout.add_widget(closeImage)

        mainLayout.add_widget(imageLayout)
# The below class is the code for button that close the full view of an image
class CloseImage(Button):
    def __init__(self, imageLayout, **kwargs):
        super(CloseImage, self).__init__(**kwargs)
        self.image_layout = imageLayout

    def on_press(self):
        mainLayout.remove_widget(self.image_layout)


# Below is the code that shows the main layout when a user open the application for the first time.
welcomeLayout = GridLayout()
welcomeLayout.size_hint = (1, None)
welcomeLayout.size = (Window.width, Window.height)
welcomeLayout.cols = 1
mainLayout.add_widget(welcomeLayout)

logo = AsyncImage()
logo.size_hint = (1,3)
try:
    logo.source = execution_path + "\\logo.png"
except:
    None
welcomeLayout.add_widget(logo)

intro = Label()
intro.font_size = 12
intro.text = "Welcome to IntelliP, your intelligent picture Gallery!"
welcomeLayout.add_widget(intro)

welcomeActionLayout = GridLayout()
welcomeActionLayout.cols = 2
welcomeActionLayout.spacing = 10
welcomeActionLayout.size_hint = (1, 2)
welcomeLayout.add_widget(welcomeActionLayout)

scanButton = ScanButton()
scanButton.size_hint = (1, None)
scanButton.text = "Scan Photos"
scanButton.font_size = 20
welcomeActionLayout.add_widget(scanButton)

aboutButton = AboutButton()
aboutButton.size_hint = (1, None)
aboutButton.text = "About"
aboutButton.font_size = 20
welcomeActionLayout.add_widget(aboutButton)

copyright = Label()
copyright.font_size = 15
copyright.text = "(c) Moses & John Olafenwa"
welcomeLayout.add_widget(copyright)


# Below is the code that defines a custom object class for storing the path, prediction and percentage
# probability of the image
class ImageObject():
    def __init__(self, label, percentage, file_path):
        self.prediction = label
        self.percentage = percentage
        self.filePath = file_path

    def getLabel(self):
        return self.prediction
    def getPercentage(self):
        return self.percentage
    def getPath(self):
        return self.filePath


# Below is the default code that runs each time the application is opened. It will only
# execute when an existing scan had been made before. This code when it runs,
# will obtain all picture categories with pictures in them and show them
# in the Application
if(os.path.exists(execution_path + "\\pictures.json")):
    with open(execution_path + "\\pictures.json") as inputFile:
        json_data = json.load(inputFile)

        animals_data = json_data["animals"]
        for eachObject in animals_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "animals"
            pictures_animals_array.append(imageDictionary)

        seaanimals_data = json_data["seaanimals"]
        for eachObject in seaanimals_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "seaanimals"
            pictures_seaanimals_array.append(imageDictionary)

        birds_data = json_data["birds"]
        for eachObject in birds_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "birds"
            pictures_birds_array.append(imageDictionary)

        objects_data = json_data["objects"]
        for eachObject in objects_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "objects"
            pictures_objects_array.append(imageDictionary)

        electronics_data = json_data["electronics"]
        for eachObject in electronics_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "electronics"
            pictures_electronics_array.append(imageDictionary)

        dresses_data = json_data["dresses"]
        for eachObject in dresses_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "dresses"
            pictures_dresses_array.append(imageDictionary)

        foods_data = json_data["foods"]
        for eachObject in foods_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "foods"
            pictures_foods_array.append(imageDictionary)

        plants_data = json_data["plants"]
        for eachObject in plants_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "plants"
            pictures_plants_array.append(imageDictionary)

        aircrafts_data = json_data["aircrafts"]
        for eachObject in aircrafts_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "aircrafts"
            pictures_aircrafts_array.append(imageDictionary)

        places_data = json_data["places"]
        for eachObject in places_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "places"
            pictures_places_array.append(imageDictionary)

        vehicles_data = json_data["vehicles"]
        for eachObject in vehicles_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "vehicles"
            pictures_vehicles_array.append(imageDictionary)

        people_data = json_data["people"]
        for eachObject in people_data:
            imageDictionary = {}
            imageDictionary["path"] = eachObject["path"]
            imageDictionary["prediction"] = eachObject["prediction"]
            imageDictionary["category"] = "people"
            pictures_people_array.append(imageDictionary)

        if (len(pictures_animals_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_animals_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Animals"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Animals", pictures_animals_array)
            loadButton.text = "View Animals"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_seaanimals_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_seaanimals_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Sea Animals"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Sea Animals", pictures_seaanimals_array)
            loadButton.text = "View Sea Animals"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)


        ## Adding the Categories to UI

        if (len(pictures_birds_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_birds_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Birds"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Birds", pictures_birds_array)
            loadButton.text = "View Birds"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_objects_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_objects_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Objects"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Objects", pictures_objects_array)
            loadButton.text = "View Objects"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_electronics_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_electronics_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Electronics"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Electronics", pictures_electronics_array)
            loadButton.text = "View Electronics"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_dresses_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_dresses_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Dresses"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Dresses", pictures_dresses_array)
            loadButton.text = "View Dresses"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_foods_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_foods_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Foods"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Foods", pictures_foods_array)
            loadButton.text = "View Foods"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_plants_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_plants_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Plants"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Plants", pictures_plants_array)
            loadButton.text = "Plants"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_aircrafts_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_aircrafts_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Aircrafts"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Aircrafts", pictures_aircrafts_array)
            loadButton.text = "View Aircrafts"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_places_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_places_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Places"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Places", pictures_places_array)
            loadButton.text = "View Places"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_vehicles_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_vehicles_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> Vehicles"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> Vehicles", pictures_vehicles_array)
            loadButton.text = "View Vehicles"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        if (len(pictures_people_array) > 0):
            categoryGrid = GridLayout(size_hint_y=None, height=400)
            categoryGrid.cols = 1

            categoryImage = AsyncImage(size_hint_y=None, height=300)
            try:
                categoryImage.source = pictures_people_array[0]["path"]
                categoryGrid.add_widget(categoryImage)
            except:
                None

            categoryLabel = Label()
            categoryLabel.text = " >>> People"
            categoryLabel.font_size = 15
            categoryGrid.add_widget(categoryLabel)

            loadButton = LoadGalleryButton(" >> People", pictures_people_array)
            loadButton.text = "View People"
            loadButton.font_size = 15
            categoryGrid.add_widget(loadButton)

            galleryGrid.add_widget(categoryGrid)

        dummyGridObject = Label()
        dummyGridObject.size_hint_y = None
        dummyGridObject.height = "100"
        dummyGridObject.text = "  . \n" \
                               "  .  \n" \
                               "  .  \n"
        galleryGrid.add_widget(dummyGridObject)

        galleryScroll.add_widget(galleryGrid)
        mainLayout.add_widget(galleryScroll)



        detailsGrid = GridLayout()
        detailsGrid.cols = 4
        detailsGrid.size_hint = (1, None)


        dummy1 = Label()
        dummy1.size_hint = (1, None)
        detailsGrid.add_widget(dummy1)

        aboutbutton = AboutButton()
        aboutbutton.text = "About"
        aboutbutton.font_size = 15
        aboutbutton.size_hint = (2, None)
        aboutbutton.height = 30
        detailsGrid.add_widget(aboutbutton)

        rescanbutton = ReScanButton(galleryScroll, detailsGrid)
        rescanbutton.text = "Re-Scan Photos"
        rescanbutton.font_size = 15
        rescanbutton.size_hint = (2, None)
        rescanbutton.height = 30
        detailsGrid.add_widget(rescanbutton)

        dummy2 = Label()
        dummy2.size_hint = (1, None)
        detailsGrid.add_widget(dummy2)

        mainLayout.add_widget(detailsGrid)









# Below is the function that executes when you click to load a category.
# It will load all the pictures in the category and show it.

def loadGallery(category_name, category_array):

    if gallerySteps > 2:
        global gallerySteps
        gallerySteps -= (gallerySteps - 1)

    actionGrid = GridLayout()

    parentScroll = Scroller(actionGrid)
    parentScroll.bar_width = 20
    parentScroll.bar_inactive_color = [0.3, 0.9, 0, 5, 0.9]
    with parentScroll.canvas.before:
        Color(0, 1, 0, 1)
        parentScroll.rect = Rectangle(size=Window.size, pos=parentScroll.pos)

    containerGrid = GridLayout(spacing=10, size_hint_y=None)
    containerGrid.cols = 2
    containerGrid.bind(minimum_height=containerGrid.setter('height'))


    pictures_object_array.clear()

    for eachObject in category_array:
        imageObject = ImageObject(eachObject["prediction"], "",
                                  eachObject["path"])
        pictures_object_array.append(imageObject)

    count = 0
    for eachImage in pictures_object_array:

        try:
            count += 1
            imageGrid = GridLayout(size_hint_y=None, height=400)
            imageGrid.cols = 1

            image1 = AsyncImage(size_hint_y=None, height=300)
            try:
                image1.source = eachImage.getPath()
                imageGrid.add_widget(image1)
            except:
                None

            label1 = Label()
            label1.text = eachImage.getLabel() + " : " + eachImage.getPercentage()
            imageGrid.add_widget(label1)

            button1 = ViewImage(eachImage.getPath(), eachImage.getLabel())
            button1.text = " View Image "
            button1.font_size = 20
            imageGrid.add_widget(button1)

            containerGrid.add_widget(imageGrid)

            if (count == 10):
                break

        except:
            continue


    actionGrid.cols = 2
    actionGrid.size_hint = (1, None)

    closeButton = CloseGallery(parentScroll, actionGrid )
    closeButton.text = " << "
    closeButton.font_size = 30
    closeButton.size_hint = (1, None)
    actionGrid.add_widget(closeButton)

    pageLabel = Label()
    pageLabel.text = "1-" + str(count) + " of " + str(len(pictures_object_array))
    pageLabel.font_size = 20
    pageLabel.size_hint = (11, None)
    actionGrid.add_widget(pageLabel)





    parentScroll.add_widget(containerGrid)
    mainLayout.add_widget(parentScroll)
    mainLayout.add_widget(actionGrid)







# The function below will load previous page of at most 10 photos when the user scroll
# to the top of the category view. It works by removing the existing photo category
# and add a new one containing new pictures.
def loadPrevious():


    if gallerySteps != 1 :
        global gallerySteps
        gallerySteps -= 2
        startingPoint = gallerySteps * 10
        endingPoint = startingPoint + 10


        actionGrid = GridLayout()

        newGalleryScroll = Scroller(actionGrid)
        newGalleryScroll.bar_width = 20
        newGalleryScroll.bar_inactive_color = [0.3, 0.9, 0, 5, 0.9]
        with newGalleryScroll.canvas.before:
            Color(0, 1, 0, 1)
            newGalleryScroll.rect = Rectangle(size=Window.size, pos=newGalleryScroll.pos)

        newGalleryGrid = GridLayout(spacing=10, size_hint_y=None)
        newGalleryGrid.cols = 2
        newGalleryGrid.bind(minimum_height=newGalleryGrid.setter('height'))
        newGalleryScroll.add_widget(newGalleryGrid)
        mainLayout.add_widget(newGalleryScroll)


        for aa in range(10):
            
            try:

                eachImage = pictures_object_array[startingPoint + aa]

                imageGrid = GridLayout(size_hint_y=None, height=400)
                imageGrid.cols = 1

                image1 = AsyncImage(size_hint_y=None, height=300)
                try:
                    image1.source = eachImage.getPath()
                    imageGrid.add_widget(image1)
                except:
                    None

                label1 = Label()
                label1.text = eachImage.getLabel() + " : " + eachImage.getPercentage()
                imageGrid.add_widget(label1)

                button1 = ViewImage(eachImage.getPath(), eachImage.getLabel())
                button1.text = " View Image "
                button1.font_size = 20
                imageGrid.add_widget(button1)

                newGalleryGrid.add_widget(imageGrid)



            except:
                continue


        actionGrid.cols = 2
        actionGrid.size_hint = (1, None)

        closeButton = CloseGallery(newGalleryScroll, actionGrid)
        closeButton.text = " << "
        closeButton.font_size = 30
        closeButton.size_hint = (1, None)
        actionGrid.add_widget(closeButton)

        pageLabel = Label()
        pageLabel.text = str(startingPoint + 1) + "-" + str(endingPoint) + " of " + str(len(pictures_object_array))
        pageLabel.font_size = 20
        pageLabel.size_hint = (11, None)
        actionGrid.add_widget(pageLabel)
        mainLayout.add_widget(actionGrid)

        global gallerySteps
        gallerySteps += 1

        return True
    else:
        return False



# The function below will load next page of at most 10 photos when the user scroll
# to the bottom of the category view. It works by removing the existing photo category
# and add a new one containing new pictures.
def loadNext():
    startingPoint =  gallerySteps * 10
    endingPoint = startingPoint + 10

    if(len(pictures_object_array) - startingPoint) > 0 and (len(pictures_object_array) - startingPoint) < 10:

        endingPoint = len(pictures_object_array)

        actionGrid = GridLayout()

        newGalleryScroll = Scroller(actionGrid)
        newGalleryScroll.bar_width = 20
        newGalleryScroll.bar_inactive_color = [0.3, 0.9, 0, 5, 0.9]
        with newGalleryScroll.canvas.before:
            Color(0, 1, 0, 1)
            newGalleryScroll.rect = Rectangle(size=Window.size, pos=newGalleryScroll.pos)

        newGalleryGrid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        newGalleryGrid.cols = 2
        newGalleryGrid.bind(minimum_height=newGalleryGrid.setter('height'))
        newGalleryScroll.add_widget(newGalleryGrid)
        mainLayout.add_widget(newGalleryScroll)



        for aa in range(endingPoint - startingPoint):

            try:

                eachImage = pictures_object_array[startingPoint + aa]

                imageGrid = GridLayout(size_hint_y=None, height=400)
                imageGrid.cols = 1

                image1 = AsyncImage(size_hint_y=None, height=300)
                try:
                    image1.source = eachImage.getPath()
                    imageGrid.add_widget(image1)
                except:
                    None

                label1 = Label()
                label1.text = eachImage.getLabel()
                imageGrid.add_widget(label1)

                button1 = ViewImage(eachImage.getPath(), eachImage.getLabel())
                button1.text = " View Image "
                button1.font_size = 20
                imageGrid.add_widget(button1)

                newGalleryGrid.add_widget(imageGrid)



            except:
                continue


        actionGrid.cols = 2
        actionGrid.size_hint = (1, None)

        closeButton = CloseGallery(newGalleryScroll, actionGrid)
        closeButton.text = " << "
        closeButton.font_size = 30
        closeButton.size_hint = (1, None)
        actionGrid.add_widget(closeButton)

        pageLabel = Label()
        pageLabel.text = str(startingPoint + 1) + "-" + str(endingPoint) + " of " + str(len(pictures_object_array))
        pageLabel.font_size = 20
        pageLabel.size_hint = (11, None)
        actionGrid.add_widget(pageLabel)
        mainLayout.add_widget(actionGrid)

        global gallerySteps
        gallerySteps += 1

        return True




    elif(len(pictures_object_array) - startingPoint) > 0 and (len(pictures_object_array) - startingPoint) >= 10:

        actionGrid = GridLayout()

        newGalleryScroll = Scroller(actionGrid)
        newGalleryScroll.bar_width = 20
        newGalleryScroll.bar_inactive_color = [0.3, 0.9, 0, 5, 0.9]
        with newGalleryScroll.canvas.before:
            Color(0, 1, 0, 1)
            newGalleryScroll.rect = Rectangle(size=Window.size, pos=newGalleryScroll.pos)

        newGalleryGrid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        newGalleryGrid.cols = 2
        newGalleryGrid.bind(minimum_height=newGalleryGrid.setter('height'))
        newGalleryScroll.add_widget(newGalleryGrid)
        mainLayout.add_widget(newGalleryScroll)





        for aa in range(10):

            try:

                eachImage = pictures_object_array[startingPoint + aa]

                imageGrid = GridLayout(size_hint_y=None, height=400)
                imageGrid.cols = 1


                image1 = AsyncImage(size_hint_y=None, height=300)
                try:
                    image1.source = eachImage.getPath()
                    imageGrid.add_widget(image1)
                except:
                    None

                label1 = Label()
                label1.text = eachImage.getLabel()
                imageGrid.add_widget(label1)

                button1 = ViewImage(eachImage.getPath(), eachImage.getLabel())
                button1.text = " View Image "
                button1.font_size = 20
                imageGrid.add_widget(button1)

                newGalleryGrid.add_widget(imageGrid)



            except:
                continue


        actionGrid.cols = 2
        actionGrid.size_hint = (1, None)

        closeButton = CloseGallery(newGalleryScroll, actionGrid)
        closeButton.text = " << "
        closeButton.font_size = 30
        closeButton.size_hint = (1, None)
        actionGrid.add_widget(closeButton)

        pageLabel = Label()
        pageLabel.text = str(startingPoint + 1) + "-" + str(endingPoint) + " of " + str(len(pictures_object_array))
        pageLabel.font_size = 20
        pageLabel.size_hint = (11, None)
        actionGrid.add_widget(pageLabel)
        mainLayout.add_widget(actionGrid)

        global gallerySteps
        gallerySteps += 1

        return True
    else:
        return False



# The code below initiates the Application window
runTouchApp(mainLayout)






