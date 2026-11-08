# Télécharger les données (A1)

1. Créez un compte Kaggle et un token API (Settings > API > Create New Token).
2. Placez `kaggle.json` dans `~/.kaggle/` (ne le committez JAMAIS).
3. Lancez :

```bash
pip install kaggle
kaggle datasets download -d ealtman2019/ibm-transactions-for-anti-money-laundering-aml -p data/raw --unzip
```

Utilisez la variante **HI-Small** (fichiers `HI-Small_Trans.csv` et `HI-Small_Patterns.txt`).
Les données ne sont pas poussées sur GitHub (voir `.gitignore`).
