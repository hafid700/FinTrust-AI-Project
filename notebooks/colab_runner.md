# Exécuter le dépôt sur Colab (quand un GPU est nécessaire)

Dans une cellule Colab :

```python
!git clone https://github.com/<utilisateur>/fintrust-ai.git
%cd fintrust-ai
!pip install -q -r requirements.txt
!python -m pytest -q
```
Puis lancez vos scripts (`!python -m src.detection.train ...`) ou importez les modules dans un notebook.
