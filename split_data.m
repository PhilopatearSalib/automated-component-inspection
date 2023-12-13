clc
clear
close all
rng(1000)
% Specify the directories where the images are stored
good_dir = 'all/good';
bad_dir = 'all/bad';

% Get a list of all files in the directories
good_files = dir(fullfile(good_dir, '*.jpg'));
bad_files = dir(fullfile(bad_dir, '*.jpg'));

% Concatenate the file lists and labels
files = [good_files; bad_files];
labels = [ones(length(good_files), 1); zeros(length(bad_files), 1)];

% Randomly permute the data
perm = randperm(length(labels));
files = files(perm);
labels = labels(perm);

% Compute the number of images in each set
num_train = round(0.7 * length(labels));
num_val = round(0.2 * length(labels));
num_test = length(labels) - num_train - num_val;

% Split the data into training, validation, and test sets
train_files = files(1:num_train);
train_labels = labels(1:num_train);
val_files = files(num_train+1:num_train+num_val);
val_labels = labels(num_train+1:num_train+num_val);
test_files = files(num_train+num_val+1:end);
test_labels = labels(num_train+num_val+1:end);

% Save the images
save_images(train_files, train_labels, 'train');
save_images(val_files, val_labels, 'val');
save_images(test_files, test_labels, 'test');

% Define a function to save the images
function save_images(files, labels, output_dir)
    for i = 1:length(files)
        if labels(i) == 1
            copyfile(fullfile(files(i).folder, files(i).name), fullfile(output_dir, 'good', files(i).name));
        else
            copyfile(fullfile(files(i).folder, files(i).name), fullfile(output_dir, 'bad', files(i).name));
        end
    end
end