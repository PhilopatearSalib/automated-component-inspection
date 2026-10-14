%RUN_PIPELINE Example data-preparation run, from raw captures to a
% train/val/test dataset ready for python/train.py.
% Edit the paths and object numbers, then run one section at a time.

addpath(genpath(fileparts(mfilename('fullpath'))));

rawRoot   = 'raw';         % Obj<N>_good / Obj<N>_bad folders from the capture station
focusRoot = 'best_focus';  % sharpest image per orientation and face
dataRoot  = 'data';        % train/ val/ test/ for training
objects   = 1:8;

good = arrayfun(@(n) sprintf('Obj%d_good', n), objects, 'UniformOutput', false);
bad  = arrayfun(@(n) sprintf('Obj%d_bad',  n), objects, 'UniformOutput', false);

%% 1. Keep the sharpest image from each focus stack
select_best_focus(rawRoot, focusRoot, [good bad]);

%% 2. Manual review
% A defect is usually visible from only some faces. Before splitting, move
% images in each Obj<N>_bad folder that show no visible damage into the
% matching Obj<N>_good folder, so the labels describe what the camera sees.

%% 3. Split each class 70/20/10 into train / val / test
split_dataset(focusRoot, dataRoot, [0.7 0.2 0.1], 1000);

%% 4. Augment the training split only
% Defective parts were the smaller class, so only they are augmented here,
% bringing the classes closer to balance.
for k = 1:numel(bad)
    augment_images(fullfile(dataRoot, 'train', bad{k}));
end
