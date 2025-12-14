# Prompt Engineering Strategy

## Multi-Agent Prompt Design

### 1. Role-Based Prompting

Each agent has specialized role, goal, and backstory to establish expertise and behavior patterns.

### 2. Chain-of-Thought Guidance

Agents receive explicit step-by-step processes:

- Research: Analyze → Search → Verify → Organize
- Writer: Review → Structure → Write → Verify
- Editor: Structure → Clarity → Polish → Final check
- SEO: Identify keywords → Optimize → Create meta → Recommend

### 3. Few-Shot Learning

Writer agent receives examples of:

- Strong introductions (hook + context + preview)
- Effective conclusions (summary + takeaways + CTA)

### 4. Quality Control Prompts

- Mandatory requirements (conclusion 100+ words, 3-5 H2 headers)
- Self-check instructions before completion
- "Never refuse" directives for resilience

### 5. Error Recovery Strategies

- Graceful degradation instructions
- Alternative approaches when primary fails
- Adaptive behavior based on available information

### 6. Context Management

- Shared memory system passes context between agents
- Each agent builds upon previous work
- No information loss between stages

## Prompt Versioning

- v1.0: Basic role definitions
- v2.0: Added chain-of-thought guidance (current)
- v2.1: Added few-shot examples
- v2.2: Enhanced error recovery

## Security Considerations

- Input sanitization prevents prompt injection
- Dangerous patterns filtered from user input
- Agent boundaries prevent cross-contamination
