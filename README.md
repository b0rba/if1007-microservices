# if1007-microservices

## Escolha do cenário

(Descrever qual o cenário escolhido, motivações, etc)

## Oportunidades

(Trazer do notion pra cá quais as oportunidades que mapeamos, bem como os pontos positivos, negativos e as opotunidades de cada uma)

## Oportunidade escolhida

(Descrever qual das oportunidades acima foi escolhida, como foi feito o processo de escolha e o porquê da escolha)

### Recursos necessários

(Descrever o que pensamos inicialmente que seriam os recursos necessários, pode-se consular o strateegia para entender o que respondemos a esta pergunta)

## Produção

(Descrever a metodolodia utilizada para planejamento das atividades, qual era a ideia de MVP que tínhamos, e como se deu o processo de produção da solução)

### Definição da regra de negócio

(Pode falar da primeira abordagem pensada, e em como foi invalidade no momento da implementação, exigindo pensar numa nova abordagem)

## Experimento

(Como fizemos para testar a solução)

## Melhorias

(Aqui podemos identificar quais são os pontos fracos da solução e como ela pode ser melhorada)

---

# Technical Details

## Resources

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [RabbitMQ](https://www.rabbitmq.com/)
- [Prometheus](https://prometheus.io/)
- [wait-for-it](https://github.com/vishnubob/wait-for-it)
- [AWS](https://aws.amazon.com/)
- [Dokku](https://dokku.com/) (used only on server)

## External services

- [Sendinblue](https://pt.sendinblue.com/) (email service)

## Mail Manager

The [mail manager](mail_manager.py) is responsible for receiving the consumer requests and interact with the Sendinblue API. It also provides a method to get the available credits of the account, that indicates how many emails we can send on the actual day.

## Consumer

The [consumer](main.py) is responsible to create two jobs on the process. One is going to run every hoour and send a specific amount of emails according to the environmental variable `SENDINBLUE_MAILS_PER_HOUR`. The other one is going to run at the end of the day, get the amount of available credits on Sendinblue and send emails according to that amount.

## Publisher

The [publisher](main_publisher.py) is responsible to publish messages on the queue. It randomly chooses a template of email to send (between 5 templates) and also randomly create the parameters of that email, for example, the mentor name and the mentoring hour. The main idea of this producer is to have a MVP that proves that the solution is working and also works as a draft for future implementations of publishers.

## Running the project

To run the project you just need to use docker compose. Run:

```bash
docker-compose up
```

### Running the publisher

First, you need to export the correct queue url. If you're running the queue locally with the [docker-compose](docker-compose.yaml), you can just run:

```bash
export QUEUE_SERVICE_URL=amqp://guest:guest@rabbitmq:5672/%2f
```

And to publish, for example, 5 messages, run:

```bash
python main_publisher.py -n 5
```

### RabbitMQ Management

The RabbitMQ service has an UI that provides some monitoring information about the queue. Running locally you can access it in http://localhost:15672

### Prometheus

We use prometheus to track 4 topics.

- `mails_sent` to count how many email requests were succesfully sent;
- `mails_fails` to count how many email requests have failed;
- `payload_template` to count how many emails of each template we have sent (The template id is the label for this topic)
- `payload_priority` to count how many emails of each priority we have sent (The priority is the label for this topic)

Running locally you can access it in http://localhost:9090

## How to deploy

**Prerequisites**

First thing, you need to have [Dokku](https://dokku.com/) installed and configured on your server. Once you have this, you can continue with the following steps:


1. On your server, add the [RabbitMQ plugin](https://github.com/dokku/dokku-rabbitmq) of dokku:

    ```bash
    sudo dokku plugin:install https://github.com/dokku/dokku-rabbitmq.git rabbitmq
    ```

1. Create a RabbitMQ service named rabbitmq:

    ```bash
    dokku rabbitmq:create rabbitmq
    ```

1. Expose the RabbitMQ service so you can access it from outside the server:

    ```bash
    dokku rabbitmq:expose rabbitmq 5672 4369 35197 15672
    ```

1. Now let's setup the prometheus service. Pull the docker image:

    ```bash
    sudo docker pull prom/prometheus
    ```

1. Create a tag of that image on dokku:

    ```bash
    sudo docker tag prom/prometheus dokku/prometheus
    ```

1. Deploy the prometheus service:

    ```bash
    dokku tags:deploy prometheus latest
    ```

1. Now let's create the app for the consumer:

    ```bash
    dokku apps:create app
    ```

1. Set the environmental variables:

    ```bash
    dokku config:set app SENDINBLUE_URL='https://api.sendinblue.com/v3' SENDINBLUE_MAILS_PER_HOUR=12 SENDINBLUE_API_KEY='<sendinblue-api-key>' QUEUE_SERVICE_URL='amqp://rabbitmq:<rabbit-mq-password>@<server-ip>:5672/rabbitmq'
    ```

    - You can get the `<sendinblue-api-key>` on your sendinblue dashboard
    - You can check what's the `<rabbit-mq-password>` inside the RabbitMQ url on the attribute dsn when you run the command `dokku rabbitmq:info rabbitmq`

1. Now, on your local machine you need to add the dokku remote to push it using git:

    ```bash
    git remote add dokku dokku@<server-ip>:app
    ```

1. And finally deploy it with:

    ```bash
    git push dokku master
    ```
