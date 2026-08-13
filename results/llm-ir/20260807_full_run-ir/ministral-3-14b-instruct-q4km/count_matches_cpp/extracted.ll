; ModuleID = '/home/tijl/code/llmO/SUT/count_matches.cpp'
source_filename = "/home/tijl/code/llmO/SUT/count_matches.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: read) uwtable
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
  %cmp.not5.not.i = icmp eq i64 %allowed_length, 0
  br i1 %cmp.not5.not.i, label %return, label %for.body

for.body:                                         ; preds = %for.body.lr.ph, %for.body.i
  %i.018 = phi i64 [ 0, %for.body.lr.ph ], [ %inc8, %for.body.i ]
  %arrayidx = getelementptr inbounds nuw i32, ptr %queries, i64 %i.018
  %0 = load i32, ptr %arrayidx, align 4, !tbaa !4
  %cmp.not5.not.i2 = icmp eq i64 %allowed_length, 0
  br i1 %cmp.not5.not.i2, label %return, label %for.body.i

for.body.i:                                       ; preds = %for.body, %for.body.i
  %i.06.i = phi i64 [ %inc.i, %for.body.i ], [ 0, %for.body ]
  %add.ptr.i.i = getelementptr inbounds nuw i32, ptr %allowed, i64 %i.06.i
  %1 = load i32, ptr %add.ptr.i.i, align 4, !tbaa !4
  %cmp2.i = icmp eq i32 %1, %0
  %inc.i = add nuw i64 %i.06.i, 1
  %exitcond.not.i = icmp eq i64 %inc.i, %allowed_length
  br i1 %cmp2.i, label %found, label %for.body.i, !llvm.loop !8

found:                                            ; preds = %for.body.i
  %inc8 = add nuw i64 %i.018, 1
  %exitcond.not = icmp eq i64 %inc8, %queries_length
  br i1 %exitcond.not, label %return, label %for.body, !llvm.loop !11

return:                                           ; preds = %for.body.i, %for.body, %lor.lhs.false, %entry
  %retval.0 = phi i64 [ 0, %lor.lhs.false ], [ 0, %entry ], [ 1, %found ], [ 0, %for.body ]
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
!8 = distinct !{!8, !9, !10}
!9 = !{!"llvm.loop.mustprogress"}
!10 = !{!"llvm.loop.unroll.disable"}
!11 = distinct !{!11, !9, !10}
