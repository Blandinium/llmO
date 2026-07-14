; ModuleID = '/home/tijl/code/llmO/SUT/count_matches.cpp'
source_filename = "/home/tijl/code/llmO/SUT/count_matches.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

define i64 @count_matches(ptr noundef readonly %allowed, i64 noundef %allowed_length, ptr noundef readonly %queries, i64 noundef %queries_length) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
  %cmp = icmp eq ptr %allowed, null
  %cmp1 = icmp ne i64 %allowed_length, 0
  %or.cond = and i1 %cmp, %cmp1
  br i1 %or.cond, label %return, label %lor.lhs.false

lor.lhs.false:                                    ; preds = %entry
  %cmp2 = icmp ne ptr %queries, null
  %cmp517 = icmp ne i64 %queries_length, 0
  %or.cond20 = and i1 %cmp2, %cmp517
  br i1 %or.cond20, label %for.body.lr.ph, label %return

for.body.lr.ph:                                   ; preds = %lor.lhs.false
  %allowed_vec_len = and i64 %allowed_length, -4
  %has_vec = icmp ne i64 %allowed_vec_len, 0
  %has_rem = icmp ne i64 %allowed_vec_len, %allowed_length
  br label %for.body

for.body:                                         ; preds = %for.body.lr.ph, %for.end
  %matches.019 = phi i64 [ 0, %for.body.lr.ph ], [ %spec.select, %for.end ]
  %i.018 = phi i64 [ 0, %for.body.lr.ph ], [ %inc8, %for.end ]
  %arrayidx = getelementptr inbounds nuw i32, ptr %queries, i64 %i.018
  %0 = load i32, ptr %arrayidx, align 4, !tbaa !4
  br i1 %has_vec, label %vector.ph, label %scalar.ph

vector.ph:                                        ; preds = %for.body
  %q_in = insertelement <4 x i32> poison, i32 %0, i64 0
  %q_vec = shufflevector <4 x i32> %q_in, <4 x i32> poison, <4 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.ph, %vector.body.next
  %idx = phi i64 [ 0, %vector.ph ], [ %idx.next, %vector.body.next ]
  %a_ptr = getelementptr inbounds nuw i32, ptr %allowed, i64 %idx
  %a_vec = load <4 x i32>, ptr %a_ptr, align 4, !tbaa !4
  %cmp_vec = icmp eq <4 x i32> %a_vec, %q_vec
  %mask = bitcast <4 x i1> %cmp_vec to i4
  %found = icmp ne i4 %mask, 0
  br i1 %found, label %matched, label %vector.body.next

vector.body.next:                                 ; preds = %vector.body
  %idx.next = add nuw i64 %idx, 4
  %done = icmp eq i64 %idx.next, %allowed_vec_len
  br i1 %done, label %scalar.check, label %vector.body

scalar.check:                                     ; preds = %vector.body.next
  br i1 %has_rem, label %scalar.ph, label %for.end

scalar.ph:                                        ; preds = %for.body, %scalar.check
  %scalar.idx = phi i64 [ 0, %for.body ], [ %allowed_vec_len, %scalar.check ]
  br label %scalar.body

scalar.body:                                      ; preds = %scalar.ph, %scalar.body.next
  %i.06.i = phi i64 [ %scalar.idx, %scalar.ph ], [ %inc.i, %scalar.body.next ]
  %add.ptr.i.i = getelementptr inbounds nuw i32, ptr %allowed, i64 %i.06.i
  %1 = load i32, ptr %add.ptr.i.i, align 4, !tbaa !4
  %cmp2.i = icmp eq i32 %1, %0
  br i1 %cmp2.i, label %matched, label %scalar.body.next

scalar.body.next:                                 ; preds = %scalar.body
  %inc.i = add nuw i64 %i.06.i, 1
  %exitcond.not.i = icmp eq i64 %inc.i, %allowed_length
  br i1 %exitcond.not.i, label %for.end, label %scalar.body

matched:                                          ; preds = %vector.body, %scalar.body
  br label %for.end

for.end:                                          ; preds = %scalar.check, %scalar.body.next, %matched
  %match_val = phi i64 [ 1, %matched ], [ 0, %scalar.body.next ], [ 0, %scalar.check ]
  %spec.select = add nuw i64 %matches.019, %match_val
  %inc8 = add nuw i64 %i.018, 1
  %exitcond.not = icmp eq i64 %inc8, %queries_length
  br i1 %exitcond.not, label %return, label %for.body

return:                                           ; preds = %for.end, %entry, %lor.lhs.false
  %retval.0 = phi i64 [ 0, %lor.lhs.false ], [ 0, %entry ], [ %spec.select, %for.end ]
  ret i64 %retval.0
}

declare i32 @__gxx_personality_v0(...)

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: read) uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
!4 = !{!5, !5, i64 0}
!5 = !{!"int", !6, i64 0}
!6 = !{!"omnipotent char", !7, i64 0}
!7 = !{!"Simple C++ TBAA"}
