# Debug Test Files

Acest director conține fișierele de test specifice create în timpul procesului de debugging și QA.

## Conținut

### Fișiere de test Python
- `test_150_25.py` - Test pentru cazul specific 150^25
- `test_fresh.py` - Test fresh pentru validarea funcționalității
- `test_original.py` - Test original pentru comparație
- `test_overflow.py` - Test pentru overflow protection
- `test_protection.py` - Test pentru validarea protecțiilor implementate
- `test_simple.py` - Teste simple pentru verificări rapide

### Fișiere de date test
- `test_large.json` - Date de test pentru valori mari
- `test_power.json` - Date de test pentru operații de putere

## Scopul

Aceste fișiere au fost create pentru:
1. Investigarea și reproducerea bug-urilor
2. Validarea fix-urilor implementate
3. Testarea cazurilor extreme
4. Documentarea comportamentului sistemului

## Notă

Acestea sunt fișiere de debugging și nu fac parte din suita oficială de teste (src/tests/).
