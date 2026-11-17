# WAMBU-001 | Registo de decisão científica: painel independente de agentes de IA

**Data de referência:** 16 de novembro de 2026.  
**Objeto:** análise independente entre fornecedores de LLM do artigo exploratório `CONSOLIDATED_EXPLORATORY_REPORT_2026-11-16_EN_GB.md`.  
**Autoridade final:** exclusivamente o autor humano.  
**Decisão final do autor:** **PENDENTE**.

## 1. O que foi executado de facto

Foram feitas **quatro chamadas reais** a quatro LLMs de fornecedores diferentes, usando prompts cegos entre revisores, sobre evidências do manuscrito e dos relatórios experimentais. Depois, numa execução de recuperação devidamente identificada, foi feita **uma única chamada adicional** a um quinto LLM coordenador. Não houve repetição dos quatro pareceres originais.

- Execução original: [GitHub Actions #44009705898](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44009705898). Estado **FAILURE**, quatro respostas com IDs de fornecedor, **0/4** validações segundo o contrato estrito original. [Artefacto original #14296356384](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44009705898/artifacts/14296356384), SHA-256 ZIP `aa1d0adb68bee1f1a4b058daed561247f270ef296b6296da8271e9455369befd`. Um defeito de programação ao lidar com um parecer `null` impediu a chamada original à presidência do painel; essa execução não produziu o parecer colegiado esperado.
- Recuperação: [GitHub Actions #44010165893](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44010165893). Estado **SUCCESS** em termos de execução técnica e integridade dos ficheiros. Conservou as quatro respostas originais e chamou o quinto modelo **uma única vez**. [Artefacto #14296675901](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44010165893/artifacts/14296675901), SHA-256 ZIP `2b39eb0909c9af536f71d62def3b33c48004111f48680b1ddfa9828de97fe797`.
- Os hashes originais do ficheiro de metadados `23eabe00141e583cb03f4b7563aced5fc8f34a70d4c7ad98cc2694e82beb6326` e das quatro respostas `c25f6679f6c29c6a6e08c283b0b484fc55b062b78cc7069322a9b0df23287b5d` foram preservados na recuperação.

**Os cinco modelos produziram texto, mas os respetivos votos NÃO são cinco avaliações científicas formalmente qualificadas:** nenhuma das quatro respostas iniciais passou o contrato original; a resposta posterior do coordenador também falhou o esquema estrito. O resultado é **assessoria científica por IA com evidência original auditável**, não validação científica confirmatória.

## 2. Quatro revisores científicos simulados

| Papel do agente | Modelo | Recomendação encontrada no texto original | Validação estrita |
|---|---|---|---|
| Estatística e estimandos | GPT-4.1 Mini | `support_exploratory_review` | **Inválida**, `UNDECLARED_SOURCE_ID` |
| Benchmarks e comparador | Gemini 2.5 Flash | `support_exploratory_review` | **Inválida**, `REVIEW_NOT_SINGLE_JSON` |
| Proveniência e regras operacionais | DeepSeek Chat V3.1 | `support_exploratory_review` | **Inválida**, `NON_VERBATIM_EVIDENCE` |
| Novelty, ética e crítica adversarial | Claude Haiku 4.5 | `reject_scientific_claim` | **Inválida**, `REVIEW_NOT_SINGLE_JSON` |

Estas classificações são **campos literais observados nos textos brutos**, não votos aceites pelo protocolo. Não se aplica contagem de maioria, aprovação unânime, consenso científico ou fiabilidade interavaliador. A posição adversarial negativa deve ser preservada e não descartada, embora o respetivo texto não seja uma submissão íntegra e qualificada pelo validador.

## 3. Síntese coordenada, numa chamada posterior

O Qwen3 Next 80B A3B Instruct devolveu um objeto JSON com recomendação textual `support_exploratory_review`. Todavia, utilizou o campo `minor_objections` quando o protocolo exigia `minority_positions`. O contrato marcou **`CHAIR_SCHEMA_INVALID`**; a recomendação do coordenador fica registada como **conteúdo original recuperável, não como decisão colegiada aprovada**.

A resposta do coordenador identificou oito reparações principais e sete objeções científicas centrais. O sentido geral do seu texto é permitir **circulação crítica do relatório exploratório**, enquanto rejeita explicitamente qualquer pretensão de segurança validada, reprodução integral de Knowledge Triage, equivalência ou superioridade de método.

## 4. Objeções científicas documentadas

1. **Validade de referência:** faltam casos naturalísticos de autorização de agentes com decisão correta fixada por adjudicadores humanos independentes; um resultado de `merged` num PR não equivale a cumprimento de política.
2. **Fidelidade do comparador:** os testes com operadores originais do Knowledge Triage não são a execução integral do modelo publicado (classificador, embeddings, adjudicação, SafetyMargin, avaliação completa).
3. **Confundimento de informação:** o registo autoritativo recebe informações políticas atuais que as janelas recentes ou histórias compactadas não recebem de forma equivalente. Isso não isola diferenças intrínsecas de memória.
4. **Ceiling e poder:** várias sondas de ativação/revogação saturaram; quatro ou oito episódios independentes e seis questões LongMemEval não demonstram equivalência nem sustentam classificação robusta de modelos.
5. **Falhas de fornecedor e de contrato:** HTTP 429 e saídas de JSON/citação inválidas causaram dados em falta não aleatórios. Os resultados originais devem permanecer falhados ou parciais.
6. **Proveniência temporal:** PRs de Python/Rust e alterações de código são reais, mas os corpos, diffs e textos normativos recuperados retrospectivamente podem não representar o estado aplicável na data da decisão.
7. **Originalidade:** a contribuição distinta de Knowledge Triage, Supersede, ACON e LongMemEval ainda exige avaliação metodológica substantiva; o texto não pode apresentar uma inovação comprovada.
8. **Ética/editorial:** falta confirmar licenças para redistribuição, privacidade dos comentadores públicos, declarações de interesse, afiliação, autoria, modelo editorial e anonimização para revista.

Estas objeções foram derivadas dos pareceres brutos e da síntese recuperada. A existência de objeções coerentes **não prova que todos os seus detalhes são corretos**; permanecem para julgamento e possível verificação independente pelo autor.

## 5. Decisão científica provisória que a evidência permite

**Resultado observado do processo conduzido por IA:**

> O artigo está apto para ser discutido como um estudo **exploratório de resultados mistos e nulos**. Há críticas suficientes para impedir, neste estado, uma declaração de confirmação científica independente, validação de segurança operacional, reprodução integral do comparador original ou submissão como resultado confirmatório. O texto bruto do coordenador sugeriu permitir revisão exploratória, mas **não foi validado integralmente pelo contrato**.

**Classificação formal:** `AI_ADVISORY_ORIGINAL_STRICT_PARTIAL_POSTHOC_CHAIR_SCHEMA_INVALID_AUTHOR_FINAL_PENDING`.  
**Confirmação científica independente:** **NÃO ESTABELECIDA**.  
**Revisão humana independente:** **NÃO REALIZADA**.  
**Amostra confirmatória protegida:** **NÃO ACEDIDA**.  
**Submissão à revista:** **NÃO REALIZADA**.

## 6. Parecer exclusivo do autor (não preenchido)

| Campo de decisão | Situação |
|---|---|
| **Parecer final do autor** | **PENDENTE** |
| Data, assinatura/declaração e versão exata aprovada | PENDENTE |
| Aceita a circulação do relatório exploratório? | PENDENTE |
| Solicita correções aos pontos 1–8? | PENDENTE |
| Considera a contribuição científica suficiente para revista indexada? | PENDENTE |
| Aprova um protocolo confirmatório específico e imutável? | **NÃO AUTORIZADO** |
| Autoriza abertura da amostra protegida? | **NÃO** |
| Autoriza submissão externa? | **NÃO** |

O autor pode aprovar a **circulação crítica do estudo exploratório**, solicitar **revisões maiores**, rejeitar os resultados como insuficientes ou posteriormente aprovar um **protocolo confirmatório específico com hash**. Nenhuma destas decisões foi presumida. O autor humano continua a ser a única autoridade sobre o parecer final.

## 7. Rastreabilidade e próximos passos

O registo estruturado está em [`editorial/P10_AI_ADVISORY_OBSERVED_DECISION_2026-11-16.json`](../editorial/P10_AI_ADVISORY_OBSERVED_DECISION_2026-11-16.json). O protocolo original está em [`protocol/P10_AI_MANAGED_SCIENTIFIC_REVIEW_V1.json`](../protocol/P10_AI_MANAGED_SCIENTIFIC_REVIEW_V1.json). O manuscrito avaliado foi [`CONSOLIDATED_EXPLORATORY_REPORT_2026-11-16_EN_GB.md`](../manuscript/CONSOLIDATED_EXPLORATORY_REPORT_2026-11-16_EN_GB.md).

O próximo trabalho cientificamente elegível para uma **conclusão confirmatória** continua a ser qualificar P07/P08 e um instrumento discriminativo com informação comparável, seguidos de protocolo prospectivo congelado e aprovação específica do autor. A avaliação por agentes de IA é útil para identificar falhas, não para fabricar independência humana ou ultrapassar essas condições.

**Estado de decisão:** `AGENTES_DOCUMENTADOS; OBRIGAÇÕES_CIENTÍFICAS_PENDENTES; PARECER_FINAL_EXCLUSIVO_DO_AUTOR`.
