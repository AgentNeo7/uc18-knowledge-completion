@IsTest private class KnowledgeGapDraftActionTest {
 @IsTest static void outputRemainsDraft() {Case c=new Case(Subject='Synthetic guidance gap',Status='New',Origin='Phone');insert c;KnowledgeGapDraftAction.Request r=new KnowledgeGapDraftAction.Request();r.caseId=c.Id;Integer beforeDml=Limits.getDmlStatements();KnowledgeGapDraftAction.Result v=KnowledgeGapDraftAction.draft(new List<KnowledgeGapDraftAction.Request>{r})[0];System.assertEquals('DRAFT_REQUIRES_KNOWLEDGE_OWNER',v.state);System.assert(v.draftOutline.contains('No answer generated'));System.assertEquals(beforeDml,Limits.getDmlStatements());}
 @IsTest static void absentCaseUnknown() {System.assertEquals('UNKNOWN',KnowledgeGapDraftAction.draft(new List<KnowledgeGapDraftAction.Request>{null})[0].state);}
}
