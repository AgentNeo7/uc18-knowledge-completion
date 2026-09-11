public with sharing class KnowledgeGapDraftAction {
 public class Request { @InvocableVariable(required=true) public Id caseId; }
 public class Result { @InvocableVariable public String state; @InvocableVariable public String draftOutline; @InvocableVariable public String sourceReference; }
 @InvocableMethod(label='Draft Case Knowledge Gap Outline' description='Returns review-only outline from permitted Case subject. Does not query or publish Knowledge articles.')
 public static List<Result> draft(List<Request> requests) {Set<Id> ids=new Set<Id>(); for(Request r:requests) if(r!=null && r.caseId!=null) ids.add(r.caseId);
  Map<Id,Case> rows=new Map<Id,Case>([SELECT Id,Subject,Reason FROM Case WHERE Id IN :ids WITH USER_MODE]); List<Result> out=new List<Result>();
  for(Request r:requests) {Result v=new Result(); Case c=r==null?null:rows.get(r.caseId); v.state='UNKNOWN'; if(c!=null) {v.state='DRAFT_REQUIRES_KNOWLEDGE_OWNER'; v.sourceReference='/lightning/r/Case/'+c.Id+'/view'; v.draftOutline='Question: '+c.Subject+'\nCategory hypothesis: '+(String.isBlank(c.Reason)?'Unknown':c.Reason)+'\nRequired review: existing Knowledge__kav match; authoritative answer; data categories; channel; approval. No answer generated.';} out.add(v);} return out;
 }
}
