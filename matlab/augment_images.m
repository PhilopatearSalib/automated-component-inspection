function augment_images(imgDir, pattern, varargin)
%AUGMENT_IMAGES Write flipped, noisy and rotated copies of images.
%   Copies are saved next to the originals as <name>_flipH, _flipV, _noisy
%   and _rot<angle>. Run this on the TRAINING split only, after
%   split_dataset, so augmented copies never reach validation or test.
%
%   augment_images(imgDir)                       all *.jpg, default options
%   augment_images(imgDir, pattern, Name, Value)
%
%   Options
%     'Flip'    write horizontal and vertical flips   (default true)
%     'Noise'   write a Gaussian-noise copy           (default true)
%     'Angles'  rotation angles in degrees            (default [30 180])
%
%   The defaults are the general augmentation. Under-represented classes
%   were oversampled further by rotating copies that already exist, e.g.
%     augment_images('data/train/Obj10_bad', '*noisy*.jpg', ...
%                    'Flip', false, 'Noise', false, 'Angles', [15 25 30 180])

if nargin < 2 || isempty(pattern), pattern = '*.jpg'; end
p = inputParser;
addParameter(p, 'Flip', true);
addParameter(p, 'Noise', true);
addParameter(p, 'Angles', [30 180]);
parse(p, varargin{:});
opt = p.Results;

% The listing is taken once, so new copies are not augmented again.
files = dir(fullfile(imgDir, pattern));
for k = 1:numel(files)
    img = imread(fullfile(imgDir, files(k).name));
    [~, name, ext] = fileparts(files(k).name);
    writeCopy = @(im, suffix) imwrite(im, fullfile(imgDir, [name suffix ext]));

    if opt.Flip
        writeCopy(flip(img, 2), '_flipH');
        writeCopy(flip(img, 1), '_flipV');
    end
    if opt.Noise
        writeCopy(imnoise(img, 'gaussian'), '_noisy');
    end
    for angle = opt.Angles
        writeCopy(imrotate(img, angle, 'bilinear', 'crop'), sprintf('_rot%d', angle));
    end
end
fprintf('Augmented %d images in %s\n', numel(files), imgDir);
end
