function split_dataset(inputDir, outputDir, ratios, seed)
%SPLIT_DATASET Split class folders into train / val / test, class by class.
%   inputDir holds one sub-folder per class (Obj1_good, Obj1_bad, ...).
%   Each class is shuffled and split on its own, so every class keeps the
%   same proportions in each split. Output: outputDir/{train,val,test}/<class>.
%
%   Run this BEFORE augmentation, so augmented copies of an image can never
%   land in a different split from the original.
%
%   split_dataset('best_focus', 'data')                    70/20/10, seed 1000
%   split_dataset('best_focus', 'data', [0.7 0.2 0.1], 1000)

if nargin < 3 || isempty(ratios), ratios = [0.7 0.2 0.1]; end
if nargin < 4 || isempty(seed),   seed = 1000;              end
assert(numel(ratios) == 3 && abs(sum(ratios) - 1) < 1e-9, ...
       'ratios must be [train val test] and sum to 1');
rng(seed);

splits = {'train', 'val', 'test'};
classes = dir(inputDir);
classes = classes([classes.isdir] & ~startsWith({classes.name}, '.'));

for c = 1:numel(classes)
    cls = classes(c).name;
    files = dir(fullfile(inputDir, cls, '*.jpg'));
    files = files(randperm(numel(files)));
    n = numel(files);
    nTrain = round(ratios(1) * n);
    nVal = round(ratios(2) * n);
    bounds = [0, nTrain, nTrain + nVal, n];

    for s = 1:3
        dest = fullfile(outputDir, splits{s}, cls);
        if ~exist(dest, 'dir')
            mkdir(dest);
        end
        for i = bounds(s) + 1 : bounds(s + 1)
            copyfile(fullfile(files(i).folder, files(i).name), fullfile(dest, files(i).name));
        end
    end
    fprintf('%-16s train %4d | val %4d | test %4d\n', cls, nTrain, nVal, n - nTrain - nVal);
end
end
