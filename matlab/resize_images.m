function resize_images(folderPath, pattern, outputSize)
%RESIZE_IMAGES Resize every image matching PATTERN in FOLDERPATH, in place.
%   Overwrites the originals, so run it on a copy.
%
%   resize_images('data/train/Obj1_bad')                   all *.jpg to 512x512
%   resize_images('data/train/Obj1_bad', '*.jpg', 256)

if nargin < 2 || isempty(pattern),    pattern = '*.jpg';     end
if nargin < 3 || isempty(outputSize), outputSize = [512 512]; end
if isscalar(outputSize), outputSize = [outputSize outputSize]; end

files = dir(fullfile(folderPath, pattern));
for k = 1:numel(files)
    f = fullfile(folderPath, files(k).name);
    imwrite(imresize(imread(f), outputSize), f);
end
fprintf('Resized %d images in %s\n', numel(files), folderPath);
end
