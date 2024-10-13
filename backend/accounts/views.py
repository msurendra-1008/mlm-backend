from django.http import HttpResponse

# Create your views here.
def main(request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f0f0f0;
            }
            .container {
                text-align: center;
                padding: 2rem;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #4a4a4a;
            }
            p {
                color: #6a6a6a;
            }
            .party-image {
                font-size: 5rem;
                margin-bottom: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
        <div class="party-image">🎉</div>
            <h1>Project is up and running!</h1>
            <p>Successfully deployed!</p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)
