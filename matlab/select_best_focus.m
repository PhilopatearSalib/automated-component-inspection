function select_best_focus(inputRoot, outputRoot, folders, varargin)
%SELECT_BEST_FOCUS Crop and resize captures, keeping the sharpest of each focus stack.
%   Images in each object folder are grouped by orientation (Or<N>) and
%   face/camera (f<N> or face<N>) from the file name. When a group is a focus
%   stack (several lens positions), the image with the highest focus score
%   inside a fixed region of interest is kept; a group of one image is kept
%   as is. The kept image is centre-cropped, resized and written to
%   outputRoot/<folder>/.
%
%   select_best_focus(inputRoot, outputRoot, folders)
%   select_best_focus(..., Name, Value)
%
%   Options
%     'ROI'         [x y w h] region used to score focus  (default [1800 1900 1000 600])
%     'CropSize'    side of the centre crop, in pixels      (default 2000)
%     'OutputSize'  side of the saved image, in pixels      (default 512)
%     'Measure'     focus operator, see operators.txt       (default 'GRAT')
%
%   Example
%     select_best_focus('raw', 'best_focus', {'Obj1_good', 'Obj1_bad'})
%
%   Requires fmeasure.m (third_party/fmeasure) on the MATLAB path.

p = inputParser;
addParameter(p, 'ROI', [1800 1900 1000 600]);
addParameter(p, 'CropSize', 2000);
addParameter(p, 'OutputSize', 512);
addParameter(p, 'Measure', 'GRAT');
parse(p, varargin{:});
opt = p.Results;

if ischar(folders) || isstring(folders)
    folders = cellstr(folders);
end

for d = 1:numel(folders)
    folderPath = fullfile(inputRoot, folders{d});
    files = dir(fullfile(folderPath, '*.jpg'));
    if isempty(files)
        warning('No .jpg images found in %s', folderPath);
        continue
    end

    % Group by orientation and face, e.g. Obj5_good_Or3_f2_... -> o3-f2.
    % Matching whole numbers stops Or1 from also picking up Or10 to Or12.
    tokens = regexp({files.name}, 'Or(\d+)\D*?f(?:ace)?(\d+)', 'tokens', 'once');
    keep = ~cellfun(@isempty, tokens);
    files = files(keep);
    tokens = tokens(keep);
    keys = cellfun(@(t) sprintf('o%d-f%d', str2double(t{1}), str2double(t{2})), ...
                   tokens, 'UniformOutput', false);
    [groups, ~, groupIdx] = unique(keys);

    outDir = fullfile(outputRoot, folders{d});
    if ~exist(outDir, 'dir')
        mkdir(outDir);
    end
    baseName = strrep(strrep(folders{d}, '/', '-'), '\', '-');

    for g = 1:numel(groups)
        stack = files(groupIdx == g);
        scores = zeros(1, numel(stack));
        for i = 1:numel(stack)
            img = imread(fullfile(folderPath, stack(i).name));
            if size(img, 3) == 3
                img = rgb2gray(img);
            end
            img = imcrop(im2double(img), opt.ROI);
            scores(i) = fmeasure(img, opt.Measure, []);
        end
        [~, best] = max(scores);

        img = imread(fullfile(folderPath, stack(best).name));
        win = centerCropWindow2d(size(img), [opt.CropSize opt.CropSize]);
        img = imresize(imcrop(img, win), [opt.OutputSize opt.OutputSize]);
        imwrite(img, fullfile(outDir, sprintf('%s-%s.jpg', baseName, groups{g})));
    end
    fprintf('%-16s %d views from %d images\n', folders{d}, numel(groups), numel(files));
end
end
