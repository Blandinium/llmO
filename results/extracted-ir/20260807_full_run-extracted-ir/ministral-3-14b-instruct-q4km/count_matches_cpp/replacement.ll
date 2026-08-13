define i64 @count_matches(ptr noundef readonly %allowed, i64 noundef %allowed_length, ptr noundef readonly %queries, i64 noundef %queries_length) local_unnamed_addr #0 {
entry:
  %cmp = icmp eq ptr %allowed, null
  %cmp1 = icmp ne i64 %allowed_length, 0
  %or.cond = and i1 %cmp, %cmp1
  br i1 %or.cond, label %return, label %lor.lhs.false

lor.lhs.false:
  %cmp2 = icmp eq ptr %queries, null
  %cmp517 = icmp ne i64 %queries_length, 0
  %or.cond20 = and i1 %cmp2, %cmp517
  br i1 %or.cond20, label %for.body.lr.ph, label %return

for.body.lr.ph:
  %i.018 = phi i64 [ 0, %lor.lhs.false ], [ %inc8, %for.body ]
  %matches.019 = phi i64 [ 0, %lor.lhs.false ], [ %spec.select, %for.body ]
  %cmp.not5.not.i = icmp eq i64 %allowed_length, 0
  br i1 %cmp.not5.not.i, label %return, label %for.body

for.body:
  %i.06.i = phi i64 [ 0, %for.body.lr.ph ], [ %inc.i, %for.body.i ]
  %arrayidx = getelementptr inbounds nuw i32, ptr %queries, i64 %i.018
  %query_val = load i32, ptr %arrayidx, align 4, !tbaa !4
  %found = icmp eq i64 %allowed_length, 0
  br i1 %found, label %return, label %for.body.i

for.body.i:
  %add.ptr.i.i = getelementptr inbounds nuw i32, ptr %allowed, i64 %i.06.i
  %allowed_val = load i32, ptr %add.ptr.i.i, align 4, !tbaa !4
  %cmp2.i = icmp eq i32 %allowed_val, %query_val
  %inc.i = add nuw i64 %i.06.i, 1
  %exitcond.not.i = icmp eq i64 %inc.i, %allowed_length
  %or.cond.i = select i1 %cmp2.i, i1 true, i1 %exitcond.not.i
  br i1 %or.cond.i, label %for.body.exit, label %for.body.i, !llvm.loop !8

for.body.exit:
  %spec.select = add i64 %matches.019, 1
  %inc8 = add nuw i64 %i.018, 1
  %exitcond.not = icmp eq i64 %inc8, %queries_length
  br i1 %exitcond.not, label %return, label %for.body, !llvm.loop !11

return:
  %retval.0 = phi i64 [ 0, %lor.lhs.false ], [ 0, %entry ], [ %matches.019, %for.body.lr.ph ], [ %spec.select, %for.body.exit ]
  ret i64 %retval.0
}
