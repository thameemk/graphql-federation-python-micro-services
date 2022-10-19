sudo apt update
sudo apt install nodejs git npm python3 python3-pip
git clone https://github.com/thameemk612/apollo-federation-python-micro-services.git
cd apollo-federation-python-micro-services/apollo-gateway || exit
npm install
cd ../python-app-1 || exit
python3 -m pip install virtualenv
python3 -m virtualenv venv
source venv/bin/activate
pip3 install pipenv
pipenv install


