%apply on original folders to get "best focus, cropped and resized"
clc
clear 
close all
% N = 8; % number of depth images
bfigure = false;

% metric computation 
% bren = [];
% wavv = [];
% gras = [];
% helm = [];
grat = [];

% Get the folder path where the images are stored
% folder_path = uigetdir();
% 1_good 2_bad 2_good 4_bad 4_good 5_bad 5_good 6_bad 6_good 7_bad 7_good 8_bad 8_good 9_bad 9_good 10_bad 10_good   
main_folder_path = '/Users/<redacted>/Desktop/philo/big_data';
%folders = {'Obj1_bad', 'Obj1_good', 'Obj2_bad', 'Obj2_good', 'Obj4_bad', 'Obj4_good', 'Obj5_bad', 'Obj5_good', 'Obj6_bad', 'Obj6_good', 'Obj7_bad', 'Obj7_good', 'Obj8_bad', 'Obj8_good', 'Obj9_bad', 'Obj9_good', 'Obj10_bad', 'Obj10_good'};
folders = {'Obj1_bad', 'Obj2_bad', 'Obj4_bad', 'Obj5_bad', 'Obj6_bad', 'Obj7_bad', 'Obj8_bad', 'Obj9_bad', 'Obj10_bad'};

for d = 1:length(folders)
    folder_path = fullfile(main_folder_path, folders{d});
    for o = 1:12 %orientation number
        for f = 1:4 %face number
            % Get all the image files in the folder
            pattern = sprintf('*Or%d*f%d*', o, f);
            image_files = dir(fullfile(folder_path, pattern));
            if isempty(image_files)
                continue;  % Skip to the next iteration if 'o' is not found
            end
            clear grat
            grat = [];
            for i = 1:length(image_files) 
                % Read the image
                img = imread(fullfile(folder_path, image_files(i).name));
                img = im2double(rgb2gray(img));

    %             win = centerCropWindow2d(size(img),[2500 2500]);
    %             img = imcrop(img,win);
                img = imcrop(img,[1800,1900,1000,600]);

            %     b = fmeasure(img, 'BREN', []);
            %     bren = [bren,b];

            %     w = fmeasure(img, 'WAVV', []);
            %     wavv = [wavv,w];

                gr = fmeasure(img, 'GRAT', []);
                grat = [grat,gr];
            %     
            %     gr2 = fmeasure(img, 'GRAS', []);
            %     gras = [gras,gr2];
            %     
            %     h2 = fmeasure(img, 'HELM', []);
            %     helm = [helm,h2];
            end
            if bfigure
            %     figure; plot(1:N,D); title('Derivative')
            %     figure; plot(1:N,Sm); title('Sum')
            %     figure; plot(1:N,V); title('Variance')
            %     figure; plot(1:N,bren); title('BREN')
            %     figure; plot(1:N,acmo); title('ACMO')
            %     figure; plot(1:N,gder); title('GDER')
            %     figure; plot(1:N,hise); title('HISE')
            %     figure; plot(1:N,glva); title('GLVA')
            %     figure; plot(1:N,gllv); title('GLLV')
            %     figure; plot(1:N,glvn); title('GLVN')
            %     figure; plot(1:N,wavv); title('WAVV')
        %         figure; plot(1:N,grat); title('GRAT')
            %     figure; plot(1:N,gras); title('GRAS')
            %     figure; plot(1:N,helm); title('HELM')
            end

            [M,I] = max(grat);

            best = imread([folder_path,'/',image_files(I).name]);
    %         if f == 1 || f == 3
    %             best = imcrop(best, [1000 1000 2800 2800]);
    %         else
    %             win = centerCropWindow2d(size(best),[3400 3400]);
    %             best = imcrop(best,win);
    %         end
            win = centerCropWindow2d(size(best),[2000 2000]);
            best = imcrop(best,win);
            
            %best = imresize(best, [1024 1024]);
            best = imresize(best, [256 256]);

            folder_name = extractAfter(folder_path, 'big_data/');
            file_name = strrep(folder_name, '/', '-');
            filename = sprintf('/Users/<redacted>/Desktop/philo/big_data/best_focus/%s-o%d-f%d.jpg', file_name, o, f);
            imwrite(best, filename)
        end
    end
end

