# about this repository
iOSでmanabaを使っているとき、pdfが適切にダウンロードできないため適当にダウンロードして自分用にホスティングするサービス

# how to use
docker build -t pdfnize .
docker run -p 8000:8000 pdfnize 

# settings
secrets.json に、ベーシック認証用のユーザーとパスワード、manabaのユーザーとパスワードを json で入れてください(app.py見て)。

授業資料のインターネットへの無許可の公開は駄目な可能性があるので一応認証をつけています。
