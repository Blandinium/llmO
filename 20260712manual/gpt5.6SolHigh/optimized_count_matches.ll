; ModuleID = '/home/tijl/code/llmO/SUT/count_matches.cpp'
source_filename = "/home/tijl/code/llmO/SUT/count_matches.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

define i64 @count_matches(ptr noundef readonly %allowed, i64 noundef %allowed_length, ptr noundef readonly %queries, i64 noundef %queries_length) local_unnamed_addr #0 {
entry:
%filter = alloca [32 x i64], align 16
%allowed.nonnull = icmp ne ptr %allowed, null
%queries.nonnull = icmp ne ptr %queries, null
%allowed.nonempty = icmp ne i64 %allowed_length, 0
%queries.nonempty = icmp ne i64 %queries_length, 0
%ptrs.valid = and i1 %allowed.nonnull, %queries.nonnull
%lengths.valid = and i1 %allowed.nonempty, %queries.nonempty
%valid = and i1 %ptrs.valid, %lengths.valid
br i1 %valid, label %setup, label %return

setup:
%allowed.ge32 = icmp uge i64 %allowed_length, 32
%allowed.le1024 = icmp ule i64 %allowed_length, 1024
%queries.ge8 = icmp uge i64 %queries_length, 8
%bloom.range = and i1 %allowed.ge32, %allowed.le1024
%use.bloom = and i1 %bloom.range, %queries.ge8
%vec.end = and i64 %allowed_length, -8
%has.vec = icmp ne i64 %vec.end, 0
br i1 %use.bloom, label %bloom.init, label %outer.preheader

bloom.init:
call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(256) %filter, i8 0, i64 256, i1 false)
br label %bloom.build

bloom.build:
%bi = phi i64 [ 0, %bloom.init ], [ %bi.next, %bloom.build ]
%allowed.ptr.build = getelementptr inbounds i32, ptr %allowed, i64 %bi
%allowed.value.build = load i32, ptr %allowed.ptr.build, align 4, !tbaa !4
%hash.mul.build = mul i32 %allowed.value.build, -1640531527
%hash.build = lshr i32 %hash.mul.build, 21
%word.build = lshr i32 %hash.build, 6
%bit.build = and i32 %hash.build, 63
%word.index.build = zext i32 %word.build to i64
%bit.index.build = zext i32 %bit.build to i64
%filter.ptr.build = getelementptr inbounds [32 x i64], ptr %filter, i64 0, i64 %word.index.build
%filter.old.build = load i64, ptr %filter.ptr.build, align 8
%mask.build = shl i64 1, %bit.index.build
%filter.new.build = or i64 %filter.old.build, %mask.build
store i64 %filter.new.build, ptr %filter.ptr.build, align 8
%bi.next = add nuw i64 %bi, 1
%build.done = icmp eq i64 %bi.next, %allowed_length
br i1 %build.done, label %outer.preheader, label %bloom.build

outer.preheader:
br label %outer.loop

outer.loop:
%matches = phi i64 [ 0, %outer.preheader ], [ %matches.next, %query.finish ]
%qi = phi i64 [ 0, %outer.preheader ], [ %qi.next, %query.finish ]
%query.ptr = getelementptr inbounds i32, ptr %queries, i64 %qi
%query.value = load i32, ptr %query.ptr, align 4, !tbaa !4
br i1 %use.bloom, label %bloom.check, label %scan.dispatch

bloom.check:
%hash.mul.query = mul i32 %query.value, -1640531527
%hash.query = lshr i32 %hash.mul.query, 21
%word.query = lshr i32 %hash.query, 6
%bit.query = and i32 %hash.query, 63
%word.index.query = zext i32 %word.query to i64
%bit.index.query = zext i32 %bit.query to i64
%filter.ptr.query = getelementptr inbounds [32 x i64], ptr %filter, i64 0, i64 %word.index.query
%filter.word.query = load i64, ptr %filter.ptr.query, align 8
%mask.query = shl i64 1, %bit.index.query
%filter.hit.bits = and i64 %filter.word.query, %mask.query
%filter.hit = icmp ne i64 %filter.hit.bits, 0
br i1 %filter.hit, label %scan.dispatch, label %query.nomatch

scan.dispatch:
%query.insert = insertelement <4 x i32> poison, i32 %query.value, i64 0
%query.splat = shufflevector <4 x i32> %query.insert, <4 x i32> poison, <4 x i32> zeroinitializer
br i1 %has.vec, label %vector.loop, label %scalar.preheader

vector.loop:
%vi = phi i64 [ 0, %scan.dispatch ], [ %vi.next, %vector.continue ]
%allowed.ptr.v0 = getelementptr inbounds i32, ptr %allowed, i64 %vi
%allowed.v0 = load <4 x i32>, ptr %allowed.ptr.v0, align 4
%vi.plus4 = add nuw i64 %vi, 4
%allowed.ptr.v1 = getelementptr inbounds i32, ptr %allowed, i64 %vi.plus4
%allowed.v1 = load <4 x i32>, ptr %allowed.ptr.v1, align 4
%cmp.v0 = icmp eq <4 x i32> %allowed.v0, %query.splat
%cmp.v1 = icmp eq <4 x i32> %allowed.v1, %query.splat
%cmp.v = or <4 x i1> %cmp.v0, %cmp.v1
%vector.hit = call i1 @llvm.vector.reduce.or.v4i1(<4 x i1> %cmp.v)
br i1 %vector.hit, label %query.match, label %vector.continue

vector.continue:
%vi.next = add nuw i64 %vi, 8
%vector.done = icmp eq i64 %vi.next, %vec.end
br i1 %vector.done, label %scalar.preheader, label %vector.loop

scalar.preheader:
%si.start = phi i64 [ 0, %scan.dispatch ], [ %vec.end, %vector.continue ]
%has.scalar = icmp ult i64 %si.start, %allowed_length
br i1 %has.scalar, label %scalar.loop, label %query.nomatch

scalar.loop:
%si = phi i64 [ %si.start, %scalar.preheader ], [ %si.next, %scalar.continue ]
%allowed.ptr.scalar = getelementptr inbounds i32, ptr %allowed, i64 %si
%allowed.value.scalar = load i32, ptr %allowed.ptr.scalar, align 4, !tbaa !4
%scalar.hit = icmp eq i32 %allowed.value.scalar, %query.value
%si.next = add nuw i64 %si, 1
br i1 %scalar.hit, label %query.match, label %scalar.continue

scalar.continue:
%scalar.done = icmp eq i64 %si.next, %allowed_length
br i1 %scalar.done, label %query.nomatch, label %scalar.loop

query.match:
br label %query.finish

query.nomatch:
br label %query.finish

query.finish:
%matched = phi i64 [ 1, %query.match ], [ 0, %query.nomatch ]
%matches.next = add i64 %matches, %matched
%qi.next = add nuw i64 %qi, 1
%queries.done = icmp eq i64 %qi.next, %queries_length
br i1 %queries.done, label %return, label %outer.loop

return:
%result = phi i64 [ 0, %entry ], [ %matches.next, %query.finish ]
ret i64 %result
}

declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg)
declare i1 @llvm.vector.reduce.or.v4i1(<4 x i1>)

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

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
