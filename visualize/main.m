clear all;
close all;
outfilename = websave('data.txt','http://104.131.145.75/ImagePicker/listBoundingBoxMetadata/');
data = tdfread(outfilename);

% get unique pk
pk_unique = unique(data.pk);

for i = 1:numel(pk_unique)
    pk = pk_unique(i);
    idx = find(data.pk == pk);

    image_url = strtrim(data.image_url(idx(1),:));
    I = imread(image_url);
    I = rgb2gray(I);
    I = repmat(I,1,1,3);
    
    
    for j=1:numel(idx)       
        x1 = data.x1(idx(j))+1;
        y1 = data.y1(idx(j))+1;
        x2 = data.x2(idx(j))+1;
        y2 = data.y2(idx(j))+1;
        nms= data.nms(idx(j));
        
        I(y1:y2,x1:x2,1)=200;
        
    end

    imwrite(I,sprintf('output/%d.png',pk));

end
