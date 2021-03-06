import csv
import os, sys

script_path = os.path.abspath(os.path.dirname(sys.argv[0])) # path/to/conver_annotations.py
keras_retinanet_path = os.path.abspath(os.path.join(script_path, os.pardir)) # path/to/keras-retinanet/

images_path = os.path.join(keras_retinanet_path,'data/images/')
annotations_path = os.path.join(keras_retinanet_path,'data/annotations/')
rect_annotations_path = os.path.join(keras_retinanet_path,'data/rectangular_annotations/')
sets_path = os.path.join(keras_retinanet_path,'data/sets/')

#create directory
if not os.path.exists(rect_annotations_path):
        os.makedirs(rect_annotations_path)


def is_in_set(key, ID, sets_path):
    """
    returns whether image ID is in the set path/to/data/sets/key.txt
    """
    with open(os.path.join(sets_path, key + '.txt')) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if ID == row[0]:
                return True
    return False         


data = {'all': [], 'train' : [], 'val' : [], 'test' : [], 'train_val' : []}
for root, dirs, files in os.walk(annotations_path):
    for file in files:
        if file.endswith('.csv'):
            with open(os.path.join(annotations_path, file)) as f:
                empty = True if (sum(1 for line in f) == 1) else False #check if .csv is empty # Needs to be fixed
                
            if empty:
                row = [os.path.join(images_path,file.replace('csv','png')),'','','','','']
                for key in data:
                    if is_in_set(key, file.replace('.csv',''), sets_path) == True:
                        data[key].append(row)
            else:
                with open(os.path.join(annotations_path, file)) as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        row[0] = os.path.join(images_path, file.replace('csv','png')) # path
                        radius = float(row[3])
                        row[1] = round(float(row[1]) - radius) # x0 
                        row[2] = round(float(row[2]) - radius) # y0
                        row[3] = round(float(row[1]) + 2*radius) # x1
                        row[4] = round(float(row[2]) + 2*radius) # y1
                        row.append('apple') # class

                        # Fix boxes on the fringe
                        if (row[1] < 0) : row[1] = 0
                        if (row[2] < 0) : row[2] = 0
                        if (row[3] > 307) : row[3] = 307
                        if (row[4] > 201) : row[4] = 201

                        for key in data:
                                if is_in_set(key, file.replace('.csv',''), sets_path) == True:
                                    data[key].append(row)

                        # Discard annotations that are off the image
                        #if (row[1] >= 0) and (row[2] >= 0) and (row[3] <= 307) and (row[4] <= 201):
                        #    for key in data:
                        #        if is_in_set(key, file.replace('.csv',''), sets_path) == True:
                        #            data[key].append(row)

                    
annotation_sets = {}
for key in data:
    with open(os.path.join(rect_annotations_path, key + '_annotations.csv'), mode='w') as f:
        file = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in data[key]:
            file.writerow(row)

#all__annotations = os.path.join(rect_annotations_path, 'all_annotations.csv')
#train_annotations = os.path.join(rect_annotations_path, 'train_annotations.csv')
new_classes = os.path.join(rect_annotations_path, 'classes.csv')

with open(new_classes, mode='w') as f:
    file = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    file.writerow(['apple',0])
