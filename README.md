<div align="center">

# Boreas IOT

**Plataforma Full Stack para monitoramento térmico industrial em tempo real, integrando telemetria de sensores com uma interface de alta performance.**

</div>

---

##  Stacks

* **Backend:** Python 3.12, Django 6.0.1, Django ORM
* **Frontend:** JavaScript (ES6+), Bootstrap 5, Chart.js, CSS3 (Custom Dark Theme)
* **Bancos de Dados:** SQLite (Relacional), MongoDB (Logs de Telemetria)
* **Segurança:** Autenticação baseada em níveis de acesso e validação dinâmica de credenciais.

---

## Funcionalidades Chave

* **Monitoramento Real-time:** Dashboard interativo com visualização de dados via Chart.js.
* **Arquitetura Multi-Tenant:** Gestão segregada de Matrizes, Filiais e Equipes.
* **Simulador de Sensores:** Algoritmo integrado para geração de massa de dados em tempo real.
* **UX Industrial:** Interface focada em dashboards de baixa fadiga visual e alta legibilidade.

---

##  Como Executar

### Setup do Ambiente:
```bash
python -m venv venv
# No Windows:
source venv/Scripts/activate  
# Instalação:
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver```
