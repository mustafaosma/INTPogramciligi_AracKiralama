# Araç Kiralama Web Uygulaması

Bu proje, Flask kullanılarak geliştirilmiş basit bir araç kiralama web uygulamasıdır.

## Özellikler

- Kullanıcı kayıt ve giriş sistemi
- Araç listeleme ve kiralama
- Admin paneli üzerinden araç ekleme ve kiralama geçmişini görüntüleme
- SQLite veritabanı kullanımı

## Kurulum

1. Bu projeyi klonlayın veya zip dosyasını çıkarın:

```bash
git clone <repo-link>
cd proje-dizini
```

2. Gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

3. Veritabanını başlatın:

```bash
python app.py
```

4. Uygulamayı başlatın:

```bash
python app.py
```

5. Tarayıcınızdan şu adrese gidin:

```
http://127.0.0.1:5000/
```

## Dosya Yapısı

- `app.py`: Ana uygulama dosyası
- `static/`: Araç görselleri gibi statik dosyalar
- `templates/`: HTML şablonları (eğer mevcutsa)
- `database.db`: SQLite veritabanı

## Notlar

- Varsayılan olarak admin hesabı yoktur. Giriş yapan kullanıcıya admin yetkisi elle verilebilir.
- Admin girişi için aşşağı bilgileri vereceğim
- Kullanıcı Adı:mustafaosma Şifre:MustafaO24
- Sıradan bir kullanıcıyla kayıt olduktan sonra admin girişi ile admin paneline girip sıradan kullanıcıya admin yetkisi verip admin yetkisi alabilirsiniz.
