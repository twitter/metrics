from string import Template

query2 = """
{
	organization(login: "twitter") {
    repositories(first:100, orderBy: {direction: DESC, field: UPDATED_AT}, privacy: PUBLIC) {
      edges {
        node {
          name
          pullRequests(first: 100 , orderBy: {direction: DESC, field:UPDATED_AT}, states:MERGED) {
            edges {
              node {
                closedAt
                author {
                  login
                }
              }
            }
          }
        }
      }
    }
    
	}
}
"""

query3 = Template("""
{
	user(login: $login) {
    name
		email
	}
}
""")