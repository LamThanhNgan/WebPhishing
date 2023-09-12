ENV_NAME="myenv"

echo "1. MAKE SURE YOU HAVE THE RIGHT ENVIRONMENT WITH PYTHON 3.7"
python --version
nvidia-smi
nvcc --version


echo "2. INSTALL TORCH ..."
pip install torch==1.9.1+cu111 torchvision==0.10.1+cu111 -f https://download.pytorch.org/whl/torch_stable.html

echo "3. INSTALL CYTHON & PYCOCOTOOLS"
pip install cython
pip install "git+https://github.com/philferriere/cocoapi.git#egg=pycocotools&subdirectory=PythonAPI"


echo "3. INSTALL DETECTRON2 ..."
git clone https://github.com/LamThanhNgan/detectron2-windows.git
# cd detectron2-windows
pip install -e detectron2-windows
# cd ..


echo "4. INSTALL GIT-LFS "

echo "5. INSTALL CLONE REPO PHISHPEDIA"
git clone https://github.com/LamThanhNgan/Phishpedia.git

echo "6. REPAIRING RESOURCE FOR PHISHPEDIA ..."
pip install gdown
gdown --folder "https://drive.google.com/drive/folders/1rCEqhu1CS8tphwDKoxsCRh5t1PXfSceH"           # using gdown to download phishpedia_models resource storage on drive


cp -r phishpedia_models/detectron2_pedia/* Phishpedia/phishpedia/src/detectron2_pedia               # cp phishpedia_models/detectron2_pedia to clone repo Phishpedia
cp -r phishpedia_models/siamese_pedia/* Phishpedia/phishpedia/src/siamese_pedia                     # cp phishpedia_models/siamese_pedia to clone repo Phishpedia
cp -r phishpedia_models/siamese_retrain/* Phishpedia/phishpedia/src/siamese_pedia/siamese_retrain   # cp phishpedia_models/siamese_retrain to clone repo Phishpedia
rm -rf phishpedia_models


echo "7. INSTALL PHISHPEDIA ..."
pip install -e Phishpedia

