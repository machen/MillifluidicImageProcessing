%% code for computing the Invating Matrix
%% by Marcel Moura @ PoreLab - UiO (09/2022)

directory_imges = 'G:\My Drive\Postdoctoral work\Inertial Dissolution\Experiments\SinG4_1_25mLpMin_2022_11_2\';
listOfimages = dir([directory_imges,'*.png']);

%% here we batch process the images

sz=size([2064, 2464]) %% size is a vector [height width]
invadingmatrix = zeros(sz);
current_invaded_zone = zeros(sz);


imgnumber_ini = 1
imgnumber_end = 331
imageini_name=['image_',num2str(imgnumber_ini),'.png']
xini=[directory_imges,imageini_name]; %initial image to define positions of beads, pores ect
Imgini=imread(xini);
Imgini=Imgini(:,:,1);

for img_number=imgnumber_ini+1:imgnumber_end

% img_number = 58

image_name=['image_',num2str(img_number),'.png']
x=[directory_imges,image_name];
Img=imread(x);
Img=Img(:,:,1);


Img_dif=double(Img)-double(Imgini);

Img_dif(Img_dif<threshold)=0;
Img_dif(Img_dif>=threshold)=1;

invadingmatrix(Img_dif~=0&invadingmatrix==0)=img_number;
end


%% plots of the invading matrix

figure;imagesc(invadingmatrix);colorbar;title('Invading matrix')
cmap = jet(max(invadingmatrix(:)));
% Make values 0 black:
cmap(1:1,:) = zeros(1,3);
colormap(cmap);
colorbar
c = colorbar;
first_invasion_frame=imgnumber_ini;
caxis([first_invasion_frame max(invadingmatrix_total(:))])
c.Label.String = 'Invasion frame';
axis image;


