from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd
pd.options.display.float_format = '{:,}'.format


app = Flask(__name__, template_folder='templates')

# reference dataset
house = pd.read_csv('house.csv').drop(['Unnamed: 0'], axis=1)

# loading model
kreg = joblib.load('kreg.pkl')
pca = joblib.load('pca.pkl')

@app.route('/')
def home():
    return render_template("home.html")


@app.route('/', methods=['POST', 'GET'])
def result():
    cols = ['city', 'building_area', 'land_area',
            'Bedroom', 'Bathroom', 'Sertifikat',
            'Dilengkapi Perabotan', 'Kondisi Properti', 'Jumlah Lantai',
            'lat', 'lng', ]
    if request.method == 'POST':
        test = request.form.to_dict(flat=False)
        test = pd.DataFrame(test)
        test = mapper(test)
        test = test.loc[:, cols]
        
        similar_house_index = kreg.kneighbors(
            pca.transform(test.drop(['city'], axis=1)), n_neighbors=5)[1].tolist()[0]
        
        similar_house = house.loc[similar_house_index, [
            'building_area', 'land_area', 'url', 'price']]

        test = test.assign(price_prediction=kreg.predict(
            pca.transform(test.drop(['city'], axis=1))))

        result = 'Rp{0:,}'.format(int(test['price_prediction'].tolist()[0]))
        lowest = 'Rp{0:,}'.format(similar_house.price.min())
        highest = 'Rp{0:,}'.format(similar_house.price.max())

        test = demapper(test)

        return render_template("home.html",
                               result=result,
                               lowest=lowest,
                               highest=highest,
                               similar_house=similar_house.values,
                               input_=test.to_dict(orient='records')
                               )


coordinates = pd.DataFrame({'city': ['Jakarta Utara',
                                     'Jakarta Timur',
                                     'Jakarta Selatan',
                                     'Jakarta Barat',
                                     'Jakarta Pusat', ],
                            'lat': [-6.138414,
                                    -6.225014,
                                    -6.261493,
                                    -6.168329,
                                    -6.186486],
                            'lng': [106.863956,
                                    106.900447,
                                    106.810600,
                                    106.758849,
                                    106.834091]})


def mapper(df):
    df = df.merge(coordinates, on='city')

    df['Sertifikat'] = df['Sertifikat'].map(
        {'SHM': 0,
         'HGB': 1,
         'HP': 2,
         'Lainnya': 3
         })

    df['Dilengkapi Perabotan'] = df['Dilengkapi Perabotan'].map(
        {'Unfurnished': 0,
         'Semi Furnished': 1,
         'Furnished': 2})

    df['Kondisi Properti'] = df['Kondisi Properti'].map(
        {'Baru': 0,
         'Bagus Sekali': 1,
         'Bagus': 2,
         'Sudah Renovasi': 3,
         'Butuh Renovasi': 4})

    df = df.astype({'building_area': 'float',
                    'land_area': 'float',
                    'Bedroom': 'int',
                    'Bathroom': 'int',
                    'Sertifikat': 'float',
                    'Dilengkapi Perabotan': 'float',
                    'Kondisi Properti': 'float',
                    'Jumlah Lantai': 'int',
                    'lat': 'float',
                    'lng': 'float'})

    return df


def demapper(df):

    df['city'] = df['city'].map({
        'Jakarta Timur': 'East Jakarta', 'Jakarta Selatan': 'South Jakarta',
        'Jakarta Pusat': 'Central Jakarta',
        'Jakarta Utara': 'North Jakarta', 'Jakarta Barat': 'West Jakarta'
    })

    df['Sertifikat'] = df['Sertifikat'].map(
        {0: 'SHM',
         1: 'HGB',
         2: 'HP',
         3: 'Other'
         })

    df['Dilengkapi Perabotan'] = df['Dilengkapi Perabotan'].map(
        {0: 'Unfurnished',
         1: 'Semi Furnished',
         2: 'Furnished'})

    df['Kondisi Properti'] = df['Kondisi Properti'].map(
        {0: 'New',
         1: 'Very Good',
         2: 'Good',
         3: 'Renovated',
         4: 'Need Renovation'})

    df = df.drop(['lat', 'lng'], axis=1)

    return df


if __name__ == "__main__":
    app.run(debug=True, port=5000)
