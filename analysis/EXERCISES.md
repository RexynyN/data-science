## 🧪 Lista de **30 Exercícios** para Treinar PySpark

### 🛠️ **Básico a Intermediário**

1. Ler todos os arquivos CSV usando `spark.read.csv` e inferir schema.
2. Verificar os tipos de dados de cada DataFrame e corrigir se necessário.
3. Quantos usuários únicos há na base?
4. Qual é o valor total de vendas por categoria de produto?
5. Quais os 10 produtos mais vendidos em quantidade?
6. Média de preço dos produtos por categoria.
7. Agrupe os pedidos por status e calcule a proporção de cada um.
8. Quantos pedidos cada vendedor recebeu?
9. Quais são os 10 usuários que mais compraram em valor?
10. Liste os usuários com mais de 5 avaliações feitas.
11. Quais estados têm mais usuários cadastrados?
12. Quais as formas de pagamento mais usadas?
13. Encontre o tempo médio entre a data do pedido e a avaliação.
14. Qual é a nota média dos produtos por categoria?
15. Liste os produtos com nota média maior que 4.5.

### 🔄 **Transformações Avançadas**

16. Crie uma coluna de receita por item (`price * quantity`).
17. Calcule a receita total por vendedor.
18. Junte produtos e vendedores para exibir os nomes das empresas com seus produtos.
19. Faça o join dos pedidos com os pagamentos e analise discrepâncias de valor.
20. Use `window functions` para rankear os produtos mais vendidos por categoria.
21. Calcule a média móvel de vendas por semana.
22. Encontre sessões com duração maior que 60 minutos.
23. Descubra o tempo total gasto na plataforma por usuário.
24. Liste os usuários que compraram produtos de mais de 3 categorias distintas.

### 🧠 **Análise e Machine Learning**

25. Crie buckets de valor de compra (baixo, médio, alto) e agrupe usuários.
26. Realize uma clusterização de usuários com KMeans usando gasto total e número de pedidos.
27. Classifique usuários em “ativos”, “regulares” e “inativos” com base em sessões e pedidos.
28. Detecte outliers de pagamentos usando desvio padrão.
29. Crie uma coluna "churn" (1 se o usuário não compra há 6 meses) e use para análise.
30. Modele a propensão de um usuário avaliar um pedido com base em dados históricos (classificação).


### 🧠 **Analytics, UDFs e Views**

31. Crie uma view temporária com os produtos e a receita total gerada por eles.
32. Usando `SQL`, selecione os 5 vendedores que mais faturaram.
33. Crie uma coluna categórica "tipo\_usuario" com `UDF` baseada no número de pedidos: "novo", "médio", "veterano".
34. Use `broadcast join` entre products e sellers para otimizar uma agregação.
35. Filtre as avaliações onde o review foi escrito mais de 7 dias após o pedido.
36. Agrupe os usuários por estado e calcule o ticket médio por estado.
37. Analise o percentual de usuários que fizeram ao menos 1 pedido nos últimos 30 dias.
38. Crie uma coluna com o tempo médio entre compras de cada usuário.
39. Calcule a taxa de conversão de sessões em pedidos por usuário.
40. Determine a sazonalidade mensal de vendas (agrupe por mês e ano).

### 🔄 **Manipulação de Dados Complexos**

41. Use `explode` para simular listas de interesses do usuário (mock) e agregue por interesse.
42. Identifique o produto mais bem avaliado em cada categoria com `dense_rank`.
43. Crie um DataFrame com a sequência temporal de pedidos por usuário.
44. Calcule o tempo médio de entrega considerando diferença entre `order_date` e `review_date`.
45. Crie uma coluna "tipo\_pagamento\_seguro" com um `when/otherwise` para classificar tipos.
46. Converta os campos de datas para `date` e agrupe os dados por trimestre.
47. Compare o número de produtos com avaliação acima de 4 entre os vendedores.
48. Filtre produtos que nunca foram vendidos.
49. Agrupe usuários que fizeram compras com 3 ou mais métodos de pagamento distintos.
50. Calcule o Lifetime Value (LTV) de cada usuário.

### 🧬 **Performance e Particionamento**

51. Reparticione os dados de pedidos por status para performance.
52. Escreva os produtos em Parquet particionando por categoria.
53. Crie um cache dos dados de usuários mais ativos.
54. Conte o número de joins realizados com broadcast e sem broadcast.
55. Otimize a leitura de arquivos parquet com `pushDownPredicate`.

### 🤖 **MLlib: Machine Learning em Spark**

56. Use `StringIndexer` e `VectorAssembler` para preparar dados de usuários.
57. Treine um modelo de classificação para prever se um usuário vai avaliar um produto.
58. Use `KMeans` para clusterizar vendedores baseado em volume e receita.
59. Avalie a acurácia de um modelo de classificação com `MulticlassClassificationEvaluator`.
60. Crie um pipeline completo com transformação + modelo + avaliação.