# Office of the CTO (OCTO)

# I. Introduction

The Office of the CTO (OCTO) is an organization within Global Engineering, focused on rapid innovation and technical experimentation for our most strategic technology areas. Its mission is to establish Red Hat as a leader in AI platforms, open hybrid cloud, and open source by anticipating future product and service evolution (12-36 month horizon). OCTO operates outside product engineering to address broad technological problems, potentially leading to new product directions, and uses a distinct, rapid discovery model. This organization minimizes risk and expense through its small size (1% of global engineering), adaptable individual contributors skilled in rapid prototyping across a wide array of domain areas, and short project timelines. This operational model ensures that the reward of successful projects significantly outweighs the low cost of non-viable ones.

# II. What We Do: Core Responsibilities and Offerings

OCTO is primarily focused on informing and impacting Red Hat’s long term technology strategy for both current and future addressable markets. Whereas product engineering roadmaps tend to be focused on the next 6-12 months, OCTO is focused on the next 1-3 years. In that respect, we deliver several key functions for engineering.

* **Identify** **new emerging technologies**, market trends and research topics that are relevant to Red Hat’s addressable market.  
* For the above, **drive alignment** **on a coordinated response** with the Global Engineering and Products organizations and include this perspective into Red Hat’s strategy artifacts, such as the BU/ENG strategy 6 pagers.  
* **Develop the response** using experimentation and prototyping to help refine the technology strategy. Successful prototypes and solutions are transferred to our downstream product engineering organizations [using an established playbook](https://media.pipeline.pubspoke.com/files/issue/261/PDF/pipelinepubJune2022_A1.pdf?rng=732688598).  
* **Evangelize Red Hat breakthrough innovation** to improve our customer, partner and open source contributors perception of Red Hat as the market leader in open source and AI. 

# III. How We Operate: Processes and Methodologies

Our innovation process is as follows:

- **Good ideas can come from anywhere.** The OCTO team identifies new opportunities by tracking market trends, open source innovation, leveraging Red Hat and IBM SMEs, and understanding Red Hat's market and products.  
- **We drive alignment by [producing a POV](https://docs.google.com/document/d/1ZxsrV-qAIUJ608A4oRQNm1YdRQ7HUzQbiUkv2uKnREM/edit?usp=sharing) or contributing to the BU/Eng Strategy 6 pagers**.  
- When investigating an idea, we work within OCTO and with subject matter experts in IBM and Red Hat to ensure we properly understand the subject matter, then **we prioritize ideas according to their potential strategic impact**.   
- Using the prioritized ideas, **OCTO produces a 6 month plan in January and a subsequent 6 month plan in August.** The 6 month plans reflect our focus areas (called initiatives) and the prototype projects (JIRA Epics) within them for the next 6 months.  
- **Successful prototypes are commercialized by transferring them to product engineering teams** using [a well established process and template](https://docs.google.com/document/d/1dAwrAw5e0WnYDdeuh-m0b2wOWt4YQ09UICgmhIYvHU8/edit?tab=t.0#heading=h.ga6hi7rtns3i).  
- **We communicate our technology strategy externally** via press and analyst briefings (coordinated by RH Corporate Press and Analyst relations teams), meetups, conference presentations and keynotes, our blogging platforms ([next.redhat.com](http://next.redhat.com) and [research.redhat.com](http://research.redhat.com)) and the [RH Research Quarterly printed publication](https://research.redhat.com/quarterly/).

**Staffing** \- OCTO's staffing, typically 1% of Global Engineering headcount, expands by converting interns into full-time associates rather than requesting new headcount for experienced hires. Former interns continue prototype work, led by strong emerging leaders, transferring with matured projects to product teams for commercialization, simplifying technology transfer and onboarding.

**Innovation Methodology** \- In partnership with the Mass Open Cloud, OCTO maintains an independent Research Cloud for AI and Cloud Native. This cloud runs the Red Hat portfolio and the majority of OCTOs projects run on the cloud infrastructure. This creates a feedback loop to our portfolio for emerging use cases and grounds the prototypes in a real world cloud that has both production users in the Educational sector and external researchers and OCTO using the sandbox environments for experimentation. Additionally, because we have strong influence over the data center, we’re able to use it to explore the integration of emerging infrastructure (hardware, software, networking capabilities) with our portfolio and make it available internally to all Red Hat engineers.

# IV. Where We Contribute: Impact and Value

When either evaluating or entering major new markets like AI, Red Hat is faced with the innovators dilemma. How do we invest in the new strategic things that aren’t yet revenue generating, while still sufficiently funding the existing things that provide the bulk of our revenue and not distracting the engineering teams that keep them running? Where do we create a space to create a small investment in a hedging alternative strategy should the need arise? Where do we make engineering investments that are potentially high risk, yet high reward and too speculative to distract product engineering teams from their revenue generating assignments? 

These scenarios are well suited to an independent, agile, trusted, well connected, fast moving organization that has a comprehensive understanding of Red Hat’s strategy, strengths and weaknesses and is capable of learning very, very quickly and is not encumbered by lifecycle maintenance responsibilities of the existing portfolio. That organization is OCTO. The Office of the CTO (OCTO) has a record of success in exploratory prototypes graduating to commercialization, which is attributed to a well-established process, refined over 20 years, that emphasizes asking better questions upfront. 

The entirety of OCTO is currently focused on AI and have teams working on new capabilities at every layer of the stack. We have a team of data scientists providing Post Training coaching to internal teams leveraging inferencing in our products. We have teams working on functional and non-functional (zero trust, performance, Model as a Service, etc.) agentic capabilities for our inferencing platforms. We have teams working directly at the inferencing layer (vLLM and llm-d), teams working on optionality and hardware abstractions for all classes of AI accelerators for our inference platforms and teams working on AI infrastructure and sovereignty solution blueprints for the data center as well as solution blueprints for inferencing at the Far Edge.

Some of OCTO's past contributions include:

* **Storage Capabilities:** Leading the creation of storage capabilities into Kubernetes/OpenShift, inventing the container-native storage pattern and enabling it for Ceph and Gluster, and developing a pass-through proxy for OpenShift Virtualization to leverage OpenStack Storage Vendors' adapter libraries.  
* **Security Capabilities:** Inventing SigStore and co-leading Tekton Chains crucial components of our Secure Software Supply Chain capabilities. Early identification of Open Policy Agent, authoring the OpenShift Gatekeeper Operator, and leading attestation strategy with Keylime's development and commercialization.  
* **Internal Developer Portal:** Being a major contributor to and building the initial release of Backstage/Red Hat Developer Hub.  
* **Far Edge Strategy:** Creating Microshift/Red Hat Device Edge and Flight Control/Red Hat Edge Manager.  
* **AI/ML:** Creation of OpenDataHub / OpenShift AI, Adding VectorDB and MCP support to LlamaStack and leading the observability, deployment, quickstart and a portion of the routing workstreams for the initial creation and launch of llm-d.

# V. Interdependencies with Other Teams

OCTO works with the Field CTO, Corporate Strategy and Products organization for product/market fit feedback for the ideas that we’re working on. We work with IBM Research (primarily the Hybrid Cloud and AI organization) on technology strategy alignment and prototype development. We work with open source communities and existing or potential Red Hat partners to collaborate on product prototypes or solutions. We work with an alliance of Universities in New England for our Research Cloud. OCTO does not deliver lifecycle maintenance for what we develop and so it needs to graduate to a team that is chartered to do that. As such, solutions and prototypes from OCTO will graduate to either the Ecosystems Engineering team (Solutions focused or Edge Product focused), AI Engineering (AI Product focused) or Product Engineering (All Product focused except AI).

# VI. Conclusion

The Office of the CTO (OCTO) is a small but vital cog in Red Hat’s innovation engine.
