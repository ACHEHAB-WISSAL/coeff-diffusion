from flask import Flask, request, redirect, url_for
import numpy as np

app = Flask(__name__)

# Calculer le coefficient de diffusion et l'erreur
def calculer_coefficient_diffusion(x_A, D_AB0, D_BA0, q_A, T, D_exp, q_B, a_BA, a_AB, ra, rb):
    # Fraction de solvant :
    x_B = 1 - x_A
    
    # Tau :
    tau_AB = np.exp(-a_AB / T)
    tau_BA = np.exp(-a_BA / T)
    tau_AA = 1
    tau_BB = 1
    
    # Lambda :
    lambda_A = ra ** (1 / 3)
    lambda_B = rb ** (1 / 3)
    
    # Phi :
    phi_A = x_A * lambda_A / (x_A * lambda_A + x_B * lambda_B)
    phi_B = x_B * lambda_B / (x_A * lambda_A + x_B * lambda_B)
    
    # Theta :
    theta_A = (x_A * q_A) / (x_A * q_A + x_B * q_B)
    theta_B = (x_B * q_B) / (x_A * q_A + x_B * q_B)
    theta_BA = (theta_B * tau_BA) / (theta_A * tau_AA + theta_B * tau_BA)
    theta_AB = (theta_A * tau_AB) / (theta_A * tau_AB + theta_B * tau_BB)
    theta_AA = (theta_A * tau_AA) / (theta_A * tau_AA + theta_B * tau_BA)
    theta_BB = (theta_B * tau_BB) / (theta_A * tau_AB + theta_B * tau_BB)

    # L'équation de HSU-CHEN :
    terme1 = x_B * np.log(D_AB0) + x_A * np.log(D_BA0) + 2 * (x_A * np.log(x_A / phi_A) + x_B * np.log(x_B / phi_B)) + 2 * x_A * x_B * ((phi_A / x_A) * (1 - (lambda_A / lambda_B)) + (phi_B / x_B) * (1 - (lambda_B / lambda_A)))
    terme2 = (x_B * q_A) * ((1 - theta_BA ** 2) * np.log(tau_BA) + (1 - theta_BB ** 2) * tau_AB * np.log(tau_AB)) + (x_A * q_B) * ((1 - theta_AB ** 2) * np.log(tau_AB) + (1 - theta_AA ** 2) * tau_BA * np.log(tau_BA))

    ln_D_AB = terme1 + terme2
    D_AB = np.exp(ln_D_AB)
    
    # Calcul de l'erreur
    erreur = (np.abs(D_AB - D_exp) / D_exp) * 100

    return D_AB, erreur

# Page d'accueil
@app.route('/')
def accueil():
    return """
        <html>
            <head>
                <title>Coeffient de Diffusion</title>
            </head>
            <body>
                <h1>Bonjour, c'est WISSAL ACHEHAB de PIC12</h1>
                <p>Bienvenue dans le <u>calculateur du coefficient de diffusion</u>.</p>
                <a href='/page2'><button>Suivant</button></a>
            </body>
        </html>
    """

# Page de saisie des valeurs
@app.route('/page2', methods=['GET'])
def page2():
    return """
        <html>
            <head>
                <title>Coeffient de Diffusion</title>
            </head>
            <body>
                <h1>Saisissez les valeurs</h1>
                <form action='/page3' method='post'>
                    Fraction molaire de A (x_A): <input type='text' name='x_A' value='0.25' required><br><br>
                    Coefficient de diffusion initial D_AB0: <input type='text' name='D_AB0' value='2.1e-5' required><br><br>
                    Coefficient de diffusion initial D_BA0: <input type='text' name='D_BA0' value='2.67e-5' required><br><br>
                    rA (rA): <input type='text' name='rA' value='1.4311' required><br><br>
                    rB (rB): <input type='text' name='rB' value='0.92' required><br><br>
                    D_AB_exp (DAB_exp): <input type='text' name='DAB_exp' value='1.33e-5' required><br><br>
                    Température (T): <input type='text' name='T' value='313' required><br><br>
                    a_AB (a_AB): <input type='text' name='a_AB' value='-10.7575' required><br><br>
                    a_BA (a_BA): <input type='text' name='a_BA' value='194.5302' required><br><br>
                    q_A: <input type='text' name='q_A' value='1.432' required><br><br>
                    q_B: <input type='text' name='q_B' value='1.4' required><br><br>
                    <button type='submit'>Calculer</button>
                </form>
            </body>
        </html>
    """

# Page résultat
@app.route('/page3', methods=['POST'])
def page3():
    try:
        x_A = float(request.form['x_A'].replace(',', '.'))
        D_AB0 = float(request.form['D_AB0'])
        D_BA0 = float(request.form['D_BA0'])
        rA = float(request.form['rA'])
        rB = float(request.form['rB'])
        D_AB_exp = float(request.form['DAB_exp'])
        a_AB = float(request.form['a_AB'])
        a_BA = float(request.form['a_BA'])
        T = float(request.form['T'])
        q_A = float(request.form['q_A'])
        q_B = float(request.form['q_B'])

        D_AB, erreur = calculer_coefficient_diffusion(x_A, D_AB0, D_BA0, q_A, T, D_AB_exp, q_B, a_BA, a_AB, rA, rB)
        
        return f"""
            <html>
                <head>
                    <title>Coeffient de Diffusion</title>
                </head>
                <body>
                    <h1><i>Voici le résultat final</i></h1>
                    <p>Le coefficient de diffusion D_AB est : {D_AB:.3e} cm²/s</p>
                    <p>L'erreur relative par rapport à la valeur expérimentale est : {erreur:.2f} %</p>
                    <a href="/">Retour à l'accueil</a>
                </body>
            </html>
        """
    except ValueError as e:
        return f"""
            <html>
                <head>
                    <title>Coeffient de Diffusion</title>
                </head>
                <body>
                    <h1>Valeurs invalides. Veuillez entrer des nombres valides.</h1>
                    <p>Erreur : {str(e)}</p>
                    <a href="/page2">Retour au formulaire</a>
                </body>
            </html>
        """

# Gestion des erreurs pour les routes inexistantes
@app.errorhandler(404)
def page_non_trouvee(e):
    return """
        <html>
            <head>
                <title>Coeffient de Diffusion</title>
            </head>
            <body>
                <h1>Bonjour, c'est WISSAL ACHEHAB de PIC12</h1>
                <p>Bienvenue dans le calculateur du coefficient de diffusion.</p>
                <p style='color: red;'>La page demandée n'existe pas. Vous avez été redirigé vers l'accueil.</p>
                <a href='/page2'><button>Suivant</button></a>
            </body>
        </html>
    """, 404

if __name__ == '__main__':
    app.run(debug=True)