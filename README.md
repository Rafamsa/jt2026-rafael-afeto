# Hackathon Jovens Talentos AI Builder 2026 — Seazone

**Autor:** Rafael  
**IA Utilizada (Co-piloto e Cientista de Dados):** Antigravity (AGY)

Snapshot estático do mercado imobiliário de **Itapema (SC)**, com anúncios de Airbnb e de venda (VivaReal). A análise abaixo foi conduzida utilizando os dados fornecidos para identificar as melhores oportunidades de investimento na região.

---

## 2. Análise de Faturamento

**Pergunta 1: Qual o melhor perfil de imóvel para investir na cidade?**
Olhando só para o faturamento bruto que entra, os apartamentos de 3 a 4 quartos ganham. Mas quando o custo de compra é usado para calcular o lucro real, o *sweet spot* é o de **2 quartos, especificamente no Centro**. O custo para entrar no negócio é bem menor e a liquidez de aluguel e venda é muito maior.
[Ver gráfico de Receita Média Anual por Perfil](graficos/receita_media_anual.png)

**Pergunta 2: Qual a melhor localização em termos de receita?**
O bairro **Meia Praia** é onde tem a maior quantidade de receita total, principalmente devido à quantidade gigantesca de imóveis no bairro. No entanto, quando falamos de eficiência, a receita média por imóvel no **Centro** é superior à da Meia Praia, portanto, tem maior rendimento proporcional.
[Ver Mapa de Receita por Bairros](graficos/mapa_receita_bairros.png)

**Pergunta 3: Quais características explicam as melhores receitas?**
Maior conforto garante um preço maior, ou seja, ter ar-condicionado, TV e comodidades premium aumentam diretamente a receita. Mas há um paradoxo interessante: quando falamos de um apartamento mais luxuoso, apesar da grande receita gerada e das comodidades, temos menos avaliações e menos quantidade de anfitriões "Superhosts". Afinal, o que gera o status de *Superhost* é o alto volume de aluguéis e avaliações recebidas. Propriedades mais luxuosas e caras giram menos na quantidade de aluguéis.
[Ver gráfico de Correlação de Fatores](graficos/correlacao_features.png)

---

## 3. A Quebra de Expectativa

**Pergunta 4: Se a Seazone fosse investir hoje, o que você compraria e por quê?**
Se formos pensar na melhor propriedade para comprar e investir focando apenas no maior ROI possível (risco alto e retorno alto), um apartamento de **2 a 3 quartos em Morretes** seria a melhor opção, devido ao seu retorno beirando os **9% ao ano**.

Mas, quando pensamos num bairro que vai te dar uma **maior segurança e liquidez**, o melhor é o **Centro**, entregando um ROI de **8,13% ao ano**. No fim das contas, isso tem a ver com o perfil do investidor. Pela diferença de retorno ser tão pouca (menos de 1%), eu investiria com certeza absoluta em um **apartamento de 2 quartos no Centro**.

**A Hipótese Desvalidada (Compactos não são a melhor opção):**
A ideia inicial era testar se apartamentos compactos (studio/1 quarto) na região do Centro seriam a aposta mais eficiente para a Seazone. Com tudo o que avaliamos, a resposta é não. Para evitar qualquer viés da nossa análise anterior, isolamos os dados do VivaReal com o Airbnb e a matemática cravou: a verdadeira aposta eficiente é comprar no Centro com 2 quartos. A diferença de custo para adquirir um quarto a mais é de apenas **R$ 61 mil**, mas esse imóvel maior gera mais de **R$ 10 mil extras em receita por ano**, pagando o investimento adicional em poucos anos e fugindo do metro quadrado hiperinflacionado dos compactos.

---

## 4. Reprodução Técnica

Para reproduzir os resultados e gráficos desta análise, você precisa ter o Python 3 instalado. Siga o passo a passo abaixo:

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/Rafamsa/jt2026-rafael-afeto.git
   cd jt2026-rafael-afeto
   ```
2. **Crie um ambiente virtual e ative-o:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Instale as dependências:**
   ```bash
   pip install pandas matplotlib seaborn numpy
   ```
4. **Execute o pipeline de análise (na raiz do projeto):**
   - `python main.py`: Roda toda a nossa esteira de dados de uma só vez (faturamento, bairros, correlações, ROI imobiliário) e regera os gráficos interativos automaticamente na pasta.

---

## 5. Estrutura do Projeto / Outros Processos

- `/data/`: Contém os arquivos `.csv` crus originais (detalhes, hosts, preços, malha e VivaReal).
- `/graficos/`: Todos os gráficos e mapas geográficos plotados pelas nossas análises.
- `/insight/`: Documentos `.md` com relatórios adicionais gerados durante nossa exploração de dados.
- `/ai-log/`: Nesta pasta está salvo o histórico completo (transcrição) da conversa com a Inteligência Artificial, comprovando como estruturamos a análise.
