; ModuleID = '/home/tijl/code/llmO/SUT/format_list.cpp'
source_filename = "/home/tijl/code/llmO/SUT/format_list.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

%"class.std::__cxx11::basic_string" = type { %"struct.std::__cxx11::basic_string<char>::_Alloc_hider", i64, %union.anon }
%"struct.std::__cxx11::basic_string<char>::_Alloc_hider" = type { ptr }
%union.anon = type { i64, [8 x i8] }

@__const.digits = private unnamed_addr constant [201 x i8] c"00010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899\00", align 16

; Function Attrs: mustprogress uwtable
define noundef ptr @format_list(ptr noundef readonly %input, i64 noundef %input_length) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
  %result = alloca %"class.std::__cxx11::basic_string", align 8
  %isnull = icmp eq ptr %input, null
  %haslen = icmp ne i64 %input_length, 0
  %badargs = and i1 %isnull, %haslen
  br i1 %badargs, label %return, label %init

init:                                             ; preds = %entry
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %result) #5
  %ssobuf = getelementptr inbounds nuw i8, ptr %result, i64 16
  %lenfield = getelementptr inbounds nuw i8, ptr %result, i64 8
  %use_sso = icmp ult i64 %input_length, 2
  br i1 %use_sso, label %fill.start, label %heap.calc

heap.calc:                                        ; preds = %init
  %mulov = call { i64, i1 } @llvm.umul.with.overflow.i64(i64 %input_length, i64 13)
  %mul = extractvalue { i64, i1 } %mulov, 0
  %ov1 = extractvalue { i64, i1 } %mulov, 1
  %addov = call { i64, i1 } @llvm.uadd.with.overflow.i64(i64 %mul, i64 3)
  %sum = extractvalue { i64, i1 } %addov, 0
  %ov2 = extractvalue { i64, i1 } %addov, 1
  %ov = or i1 %ov1, %ov2
  %allocsz = select i1 %ov, i64 -1, i64 %sum
  %heapbuf = invoke noalias noundef nonnull ptr @_Znwm(i64 noundef %allocsz) #6
          to label %heap.ok unwind label %lpad.alloc

heap.ok:                                          ; preds = %heap.calc
  %cap = add i64 %allocsz, -1
  br label %fill.start

fill.start:                                       ; preds = %init, %heap.ok
  %buf = phi ptr [ %ssobuf, %init ], [ %heapbuf, %heap.ok ]
  %isheap = phi i1 [ false, %init ], [ true, %heap.ok ]
  %capph = phi i64 [ 15, %init ], [ %cap, %heap.ok ]
  store i8 91, ptr %buf, align 1, !tbaa !10
  %empty = icmp eq i64 %input_length, 0
  br i1 %empty, label %close, label %loop

loop:                                             ; preds = %fill.start, %elem.done
  %i = phi i64 [ 0, %fill.start ], [ %inc, %elem.done ]
  %pos = phi i64 [ 1, %fill.start ], [ %pos.next, %elem.done ]
  %first = icmp eq i64 %i, 0
  br i1 %first, label %conv, label %sep

sep:                                              ; preds = %loop
  %sepp = getelementptr inbounds nuw i8, ptr %buf, i64 %pos
  store i16 8236, ptr %sepp, align 1
  %pos.sep = add nuw i64 %pos, 2
  br label %conv

conv:                                             ; preds = %loop, %sep
  %pos2 = phi i64 [ %pos, %loop ], [ %pos.sep, %sep ]
  %ap = getelementptr inbounds nuw i32, ptr %input, i64 %i
  %v = load i32, ptr %ap, align 4, !tbaa !15
  %signbit = lshr i32 %v, 31
  %neg64 = zext nneg i32 %signbit to i64
  %a = call i32 @llvm.abs.i32(i32 %v, i1 false)
  %c1 = icmp ult i32 %a, 10
  br i1 %c1, label %dc.done, label %dc2

dc2:                                              ; preds = %conv
  %c2 = icmp ult i32 %a, 100
  br i1 %c2, label %dc.done, label %dc3

dc3:                                              ; preds = %dc2
  %c3 = icmp ult i32 %a, 1000
  br i1 %c3, label %dc.done, label %dc4

dc4:                                              ; preds = %dc3
  %c4 = icmp ult i32 %a, 10000
  br i1 %c4, label %dc.done, label %dc5

dc5:                                              ; preds = %dc4
  %c5 = icmp ult i32 %a, 100000
  br i1 %c5, label %dc.done, label %dc6

dc6:                                              ; preds = %dc5
  %c6 = icmp ult i32 %a, 1000000
  br i1 %c6, label %dc.done, label %dc7

dc7:                                              ; preds = %dc6
  %c7 = icmp ult i32 %a, 10000000
  br i1 %c7, label %dc.done, label %dc8

dc8:                                              ; preds = %dc7
  %c8 = icmp ult i32 %a, 100000000
  br i1 %c8, label %dc.done, label %dc9

dc9:                                              ; preds = %dc8
  %c9 = icmp ult i32 %a, 1000000000
  %nd9 = select i1 %c9, i32 9, i32 10
  br label %dc.done

dc.done:                                          ; preds = %conv, %dc2, %dc3, %dc4, %dc5, %dc6, %dc7, %dc8, %dc9
  %nd = phi i32 [ 1, %conv ], [ 2, %dc2 ], [ 3, %dc3 ], [ 4, %dc4 ], [ 5, %dc5 ], [ 6, %dc6 ], [ 7, %dc7 ], [ 8, %dc8 ], [ %nd9, %dc9 ]
  %nd64 = zext nneg i32 %nd to i64
  %dst0 = getelementptr inbounds nuw i8, ptr %buf, i64 %pos2
  store i8 45, ptr %dst0, align 1, !tbaa !10
  %dst = getelementptr inbounds nuw i8, ptr %dst0, i64 %neg64
  %big = icmp ugt i32 %a, 99
  br i1 %big, label %big.pre, label %tail

big.pre:                                          ; preds = %dc.done
  %p0 = add nsw i64 %nd64, -1
  br label %big.loop

big.loop:                                         ; preds = %big.pre, %big.loop
  %av = phi i32 [ %a, %big.pre ], [ %adiv, %big.loop ]
  %pp = phi i64 [ %p0, %big.pre ], [ %pp.next, %big.loop ]
  %rem = urem i32 %av, 100
  %adiv = udiv i32 %av, 100
  %two = shl nuw nsw i32 %rem, 1
  %hi = or disjoint i32 %two, 1
  %hi64 = zext nneg i32 %hi to i64
  %tp1 = getelementptr inbounds nuw [201 x i8], ptr @__const.digits, i64 0, i64 %hi64
  %ch1 = load i8, ptr %tp1, align 1, !tbaa !10
  %dp1 = getelementptr inbounds nuw i8, ptr %dst, i64 %pp
  store i8 %ch1, ptr %dp1, align 1, !tbaa !10
  %two64 = zext nneg i32 %two to i64
  %tp0 = getelementptr inbounds nuw [201 x i8], ptr @__const.digits, i64 0, i64 %two64
  %ch0 = load i8, ptr %tp0, align 2, !tbaa !10
  %ppm1 = add nsw i64 %pp, -1
  %dp0 = getelementptr inbounds nuw i8, ptr %dst, i64 %ppm1
  store i8 %ch0, ptr %dp0, align 1, !tbaa !10
  %pp.next = add nsw i64 %pp, -2
  %cont = icmp ugt i32 %av, 9999
  br i1 %cont, label %big.loop, label %tail, !llvm.loop !20

tail:                                             ; preds = %dc.done, %big.loop
  %af = phi i32 [ %a, %dc.done ], [ %adiv, %big.loop ]
  %ge10 = icmp ugt i32 %af, 9
  br i1 %ge10, label %tail2, label %tail1

tail2:                                            ; preds = %tail
  %t2 = shl nuw nsw i32 %af, 1
  %t2h = or disjoint i32 %t2, 1
  %t2h64 = zext nneg i32 %t2h to i64
  %tph = getelementptr inbounds nuw [201 x i8], ptr @__const.digits, i64 0, i64 %t2h64
  %chh = load i8, ptr %tph, align 1, !tbaa !10
  %dph = getelementptr inbounds nuw i8, ptr %dst, i64 1
  store i8 %chh, ptr %dph, align 1, !tbaa !10
  %t264 = zext nneg i32 %t2 to i64
  %tpl = getelementptr inbounds nuw [201 x i8], ptr @__const.digits, i64 0, i64 %t264
  %chl = load i8, ptr %tpl, align 2, !tbaa !10
  br label %elem.done

tail1:                                            ; preds = %tail
  %tr = trunc nuw i32 %af to i8
  %chd = or disjoint i8 %tr, 48
  br label %elem.done

elem.done:                                        ; preds = %tail2, %tail1
  %chlast = phi i8 [ %chl, %tail2 ], [ %chd, %tail1 ]
  store i8 %chlast, ptr %dst, align 1, !tbaa !10
  %digits.end = add nuw i64 %pos2, %neg64
  %pos.next = add nuw i64 %digits.end, %nd64
  %inc = add nuw i64 %i, 1
  %done = icmp eq i64 %inc, %input_length
  br i1 %done, label %close, label %loop, !llvm.loop !24

close:                                            ; preds = %fill.start, %elem.done
  %posf = phi i64 [ 1, %fill.start ], [ %pos.next, %elem.done ]
  %closep = getelementptr inbounds nuw i8, ptr %buf, i64 %posf
  store i8 93, ptr %closep, align 1, !tbaa !10
  %slen = add nuw i64 %posf, 1
  %nulp = getelementptr inbounds nuw i8, ptr %buf, i64 %slen
  store i8 0, ptr %nulp, align 1, !tbaa !10
  store ptr %buf, ptr %result, align 8, !tbaa !14
  store i64 %slen, ptr %lenfield, align 8, !tbaa !11
  br i1 %isheap, label %setcap, label %docall

setcap:                                           ; preds = %close
  store i64 %capph, ptr %ssobuf, align 8
  br label %docall

docall:                                           ; preds = %close, %setcap
  %call = invoke noundef ptr @_Z16copy_to_c_stringRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(32) %result)
          to label %call.ok unwind label %lpad.call

call.ok:                                          ; preds = %docall
  br i1 %isheap, label %free.ok, label %fin

free.ok:                                          ; preds = %call.ok
  %delsz = add i64 %capph, 1
  call void @_ZdlPvm(ptr noundef nonnull %buf, i64 noundef %delsz) #7
  br label %fin

fin:                                              ; preds = %call.ok, %free.ok
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %result) #5
  br label %return

lpad.alloc:                                       ; preds = %heap.calc
  %lp0 = landingpad { ptr, i32 }
          catch ptr null
  %exn0 = extractvalue { ptr, i32 } %lp0, 0
  br label %eh.done

lpad.call:                                        ; preds = %docall
  %lp1 = landingpad { ptr, i32 }
          catch ptr null
  %exn1 = extractvalue { ptr, i32 } %lp1, 0
  br i1 %isheap, label %free.eh, label %eh.done

free.eh:                                          ; preds = %lpad.call
  %delsz2 = add i64 %capph, 1
  call void @_ZdlPvm(ptr noundef nonnull %buf, i64 noundef %delsz2) #7
  br label %eh.done

eh.done:                                          ; preds = %lpad.alloc, %lpad.call, %free.eh
  %exn = phi ptr [ %exn0, %lpad.alloc ], [ %exn1, %lpad.call ], [ %exn1, %free.eh ]
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %result) #5
  %bc = call ptr @__cxa_begin_catch(ptr %exn) #5
  call void @__cxa_end_catch()
  br label %return

return:                                           ; preds = %entry, %fin, %eh.done
  %retval = phi ptr [ null, %entry ], [ %call, %fin ], [ null, %eh.done ]
  ret ptr %retval
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #1

declare i32 @__gxx_personality_v0(...)

declare noundef ptr @_Z16copy_to_c_stringRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(32)) local_unnamed_addr #2

declare ptr @__cxa_begin_catch(ptr) local_unnamed_addr

declare void @__cxa_end_catch() local_unnamed_addr

; Function Attrs: nobuiltin allocsize(0)
declare noundef nonnull ptr @_Znwm(i64 noundef) local_unnamed_addr #3

; Function Attrs: nobuiltin nounwind
declare void @_ZdlPvm(ptr noundef, i64 noundef) local_unnamed_addr #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.abs.i32(i32, i1 immarg) #8

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare { i64, i1 } @llvm.umul.with.overflow.i64(i64, i64) #8

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare { i64, i1 } @llvm.uadd.with.overflow.i64(i64, i64) #8

attributes #0 = { mustprogress uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nobuiltin allocsize(0) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nobuiltin nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nounwind }
attributes #6 = { builtin allocsize(0) }
attributes #7 = { builtin nounwind }
attributes #8 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
!4 = !{!5, !6, i64 0}
!5 = !{!"_ZTSNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE12_Alloc_hiderE", !6, i64 0}
!6 = !{!"p1 omnipotent char", !7, i64 0}
!7 = !{!"any pointer", !8, i64 0}
!8 = !{!"omnipotent char", !9, i64 0}
!9 = !{!"Simple C++ TBAA"}
!10 = !{!8, !8, i64 0}
!11 = !{!12, !13, i64 8}
!12 = !{!"_ZTSNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE", !5, i64 0, !13, i64 8, !8, i64 16}
!13 = !{!"long", !8, i64 0}
!14 = !{!12, !6, i64 0}
!15 = !{!16, !16, i64 0}
!16 = !{!"int", !8, i64 0}
!20 = distinct !{!20, !21, !22}
!21 = !{!"llvm.loop.mustprogress"}
!22 = !{!"llvm.loop.unroll.disable"}
!24 = distinct !{!24, !21}
