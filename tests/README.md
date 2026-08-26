# Tests

Automatiska tester för System Modeller.

I A1 finns endast smoke tests för repositorystruktur och paketering. Domän- och schematester tillkommer successivt.


Från A4 och framåt finns regressionsprov för metamodel och schemas. `test_a5.py` verifierar kontextobjekt och relationer.

- `test_a10.py` – A10: logisk struktur, relationer och aktiverad informationsanvändning.
- `test_a12.py` – Message/Event-schema, semantik och regression.

- `test_a18.py` – Environment/DeploymentNode-schema, nodtyper, ID-prefixer och A19-reservationer.

- A22: origin-värden, schema och separation från Evidence.status.

- `test_a25.py` verifierar teknisk/semantisk projektvalidering och negativa feltest.
