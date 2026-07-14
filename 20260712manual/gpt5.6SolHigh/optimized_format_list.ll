; ModuleID = '/home/tijl/code/llmO/SUT/format_list.cpp'
source_filename = "/home/tijl/code/llmO/SUT/format_list.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

%"class.std::__cxx11::basic_string" = type { %"struct.std::__cxx11::basic_string<char>::_Alloc_hider", i64, %union.anon }
%"struct.std::__cxx11::basic_string<char>::_Alloc_hider" = type { ptr }
%union.anon = type { i64, [8 x i8] }

$__clang_call_terminate = comdat any
$_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm = comdat any
$_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7reserveEm = comdat any

@.str.4 = private unnamed_addr constant [24 x i8] c"basic_string::_M_create\00", align 1
@digits_pairs = private unnamed_addr constant [200 x i8] c"00010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899", align 16

define internal i64 @digits10_u32(i32 %v) #19 {
entry:
%c10 = icmp ult i32 %v, 10
%c100 = icmp ult i32 %v, 100
%c1000 = icmp ult i32 %v, 1000
%c10000 = icmp ult i32 %v, 10000
%c100000 = icmp ult i32 %v, 100000
%c1000000 = icmp ult i32 %v, 1000000
%c10000000 = icmp ult i32 %v, 10000000
%c100000000 = icmp ult i32 %v, 100000000
%c1000000000 = icmp ult i32 %v, 1000000000
%d9 = select i1 %c1000000000, i64 9, i64 10
%d8 = select i1 %c100000000, i64 8, i64 %d9
%d7 = select i1 %c10000000, i64 7, i64 %d8
%d6 = select i1 %c1000000, i64 6, i64 %d7
%d5 = select i1 %c100000, i64 5, i64 %d6
%d4 = select i1 %c10000, i64 4, i64 %d5
%d3 = select i1 %c1000, i64 3, i64 %d4
%d2 = select i1 %c100, i64 2, i64 %d3
%d1 = select i1 %c10, i64 1, i64 %d2
ret i64 %d1
}

define internal ptr @write_i32(ptr %dst, i32 %v) #20 {
entry:
%neg = icmp slt i32 %v, 0
%negv = sub i32 0, %v
%mag = select i1 %neg, i32 %negv, i32 %v
br i1 %neg, label %minus, label %digits

minus:
store i8 45, ptr %dst, align 1
%afterminus = getelementptr inbounds i8, ptr %dst, i64 1
br label %digits

digits:
%start = phi ptr [ %dst, %entry ], [ %afterminus, %minus ]
%ndigits = call i64 @digits10_u32(i32 %mag)
%end = getelementptr inbounds i8, ptr %start, i64 %ndigits
%large = icmp ugt i32 %mag, 99
br i1 %large, label %pair.loop, label %tail

pair.loop:
%x = phi i32 [ %mag, %digits ], [ %q, %pair.loop ]
%p = phi ptr [ %end, %digits ], [ %slot, %pair.loop ]
%q = udiv i32 %x, 100
%q100 = mul i32 %q, 100
%r = sub i32 %x, %q100
%idx32 = shl i32 %r, 1
%idx = zext i32 %idx32 to i64
%pairptr = getelementptr inbounds [200 x i8], ptr @digits_pairs, i64 0, i64 %idx
%pair = load i16, ptr %pairptr, align 1
%slot = getelementptr inbounds i8, ptr %p, i64 -2
store i16 %pair, ptr %slot, align 1
%morepairs = icmp ugt i32 %q, 99
br i1 %morepairs, label %pair.loop, label %tail.from.loop

tail.from.loop:
br label %tail

tail:
%last = phi i32 [ %mag, %digits ], [ %q, %tail.from.loop ]
%tailp = phi ptr [ %end, %digits ], [ %slot, %tail.from.loop ]
%onedigit = icmp ult i32 %last, 10
br i1 %onedigit, label %tail.one, label %tail.two

tail.one:
%c32 = add i32 %last, 48
%c = trunc i32 %c32 to i8
%onepos = getelementptr inbounds i8, ptr %tailp, i64 -1
store i8 %c, ptr %onepos, align 1
ret ptr %end

tail.two:
%lastidx32 = shl i32 %last, 1
%lastidx = zext i32 %lastidx32 to i64
%lastpairptr = getelementptr inbounds [200 x i8], ptr @digits_pairs, i64 0, i64 %lastidx
%lastpair = load i16, ptr %lastpairptr, align 1
%twopos = getelementptr inbounds i8, ptr %tailp, i64 -2
store i16 %lastpair, ptr %twopos, align 1
ret ptr %end
}

define noundef ptr @format_list(ptr noundef readonly %input, i64 noundef %input_length) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
%str = alloca %"class.std::__cxx11::basic_string", align 8
%nullin = icmp eq ptr %input, null
%nonempty = icmp ne i64 %input_length, 0
%bad = and i1 %nullin, %nonempty
br i1 %bad, label %return.null, label %count.start

count.start:
%iszero = icmp eq i64 %input_length, 0
br i1 %iszero, label %size.done.zero, label %count.loop

count.loop:
%i = phi i64 [ 0, %count.start ], [ %nexti, %count.cont ]
%total = phi i64 [ 2, %count.start ], [ %newtotal, %count.cont ]
%inptr = getelementptr inbounds i32, ptr %input, i64 %i
%v = load i32, ptr %inptr, align 4
%vneg = icmp slt i32 %v, 0
%vnegated = sub i32 0, %v
%vmag = select i1 %vneg, i32 %vnegated, i32 %v
%vdigits = call i64 @digits10_u32(i32 %vmag)
%vsign = zext i1 %vneg to i64
%vlen = add i64 %vdigits, %vsign
%notfirst = icmp ne i64 %i, 0
%sep = select i1 %notfirst, i64 2, i64 0
%addlen = add i64 %vlen, %sep
%limit = sub i64 9223372036854775807, %addlen
%overflow = icmp ugt i64 %total, %limit
br i1 %overflow, label %return.null, label %count.cont

count.cont:
%newtotal = add i64 %total, %addlen
%nexti = add i64 %i, 1
%countdone = icmp eq i64 %nexti, %input_length
br i1 %countdone, label %size.done.loop, label %count.loop

size.done.zero:
br label %size.done

size.done.loop:
br label %size.done

size.done:
%final_length = phi i64 [ 2, %size.done.zero ], [ %newtotal, %size.done.loop ]
%sso = getelementptr inbounds i8, ptr %str, i64 16
%lenptr = getelementptr inbounds i8, ptr %str, i64 8
%alloc_size = add i64 %final_length, 1
%small = icmp ule i64 %final_length, 15
br i1 %small, label %use.sso, label %use.heap

use.sso:
br label %object.init

use.heap:
%atmax = icmp eq i64 %final_length, 9223372036854775807
br i1 %atmax, label %return.null, label %alloc

alloc:
%mem = invoke noalias noundef nonnull ptr @_Znwm(i64 noundef %alloc_size)
to label %heap.ready unwind label %lpad.alloc

heap.ready:
br label %object.init

object.init:
%buffer = phi ptr [ %sso, %use.sso ], [ %mem, %heap.ready ]
%isheap = phi i1 [ false, %use.sso ], [ true, %heap.ready ]
store ptr %buffer, ptr %str, align 8
store i64 %final_length, ptr %lenptr, align 8
br i1 %isheap, label %set.capacity, label %fill.start

set.capacity:
store i64 %final_length, ptr %sso, align 8
br label %fill.start

fill.start:
store i8 91, ptr %buffer, align 1
%after.open = getelementptr inbounds i8, ptr %buffer, i64 1
%fillzero = icmp eq i64 %input_length, 0
br i1 %fillzero, label %fill.done.zero, label %fill.loop

fill.loop:
%j = phi i64 [ 0, %fill.start ], [ %nextj, %fill.cont ]
%out = phi ptr [ %after.open, %fill.start ], [ %nextout, %fill.cont ]
%used = phi i64 [ 1, %fill.start ], [ %newused, %fill.cont ]
%vinptr = getelementptr inbounds i32, ptr %input, i64 %j
%val = load i32, ptr %vinptr, align 4
%valneg = icmp slt i32 %val, 0
%valnegated = sub i32 0, %val
%valmag = select i1 %valneg, i32 %valnegated, i32 %val
%valdigits = call i64 @digits10_u32(i32 %valmag)
%valsign = zext i1 %valneg to i64
%currentlen = add i64 %valdigits, %valsign
%first = icmp eq i64 %j, 0
%currentsep = select i1 %first, i64 0, i64 2
%needed = add i64 %currentlen, %currentsep
%contentlimit = sub i64 %final_length, 1
%remaining = sub i64 %contentlimit, %used
%fits = icmp ule i64 %needed, %remaining
br i1 %fits, label %space.ok, label %build.fail

space.ok:
br i1 %first, label %write.value, label %write.sep

write.sep:
store i8 44, ptr %out, align 1
%sp = getelementptr inbounds i8, ptr %out, i64 1
store i8 32, ptr %sp, align 1
%aftersep = getelementptr inbounds i8, ptr %out, i64 2
br label %write.value

write.value:
%valuedst = phi ptr [ %out, %space.ok ], [ %aftersep, %write.sep ]
%nextout = call ptr @write_i32(ptr %valuedst, i32 %val)
br label %fill.cont

fill.cont:
%newused = add i64 %used, %needed
%nextj = add i64 %j, 1
%filldone = icmp eq i64 %nextj, %input_length
br i1 %filldone, label %fill.done.loop, label %fill.loop

build.fail:
br i1 %isheap, label %free.fail, label %return.null

free.fail:
call void @_ZdlPvm(ptr noundef %buffer, i64 noundef %alloc_size)
br label %return.null

fill.done.zero:
br label %fill.done

fill.done.loop:
br label %fill.done

fill.done:
%actualused = phi i64 [ 1, %fill.done.zero ], [ %newused, %fill.done.loop ]
%closepos = phi ptr [ %after.open, %fill.done.zero ], [ %nextout, %fill.done.loop ]
%actual_length = add i64 %actualused, 1
store i64 %actual_length, ptr %lenptr, align 8
store i8 93, ptr %closepos, align 1
%nulpos = getelementptr inbounds i8, ptr %closepos, i64 1
store i8 0, ptr %nulpos, align 1
%result = invoke noundef ptr @_Z16copy_to_c_stringRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(32) %str)
to label %copy.ok unwind label %lpad.copy

copy.ok:
br i1 %isheap, label %free.ok, label %return.result

free.ok:
call void @_ZdlPvm(ptr noundef %buffer, i64 noundef %alloc_size)
br label %return.result

return.result:
ret ptr %result

lpad.alloc:
%lp.alloc = landingpad { ptr, i32 }
catch ptr null
%exn.alloc = extractvalue { ptr, i32 } %lp.alloc, 0
br label %catch

lpad.copy:
%lp.copy = landingpad { ptr, i32 }
catch ptr null
%exn.copy = extractvalue { ptr, i32 } %lp.copy, 0
br i1 %isheap, label %free.unwind, label %catch.copy

free.unwind:
call void @_ZdlPvm(ptr noundef %buffer, i64 noundef %alloc_size)
br label %catch.copy

catch.copy:
br label %catch

catch:
%exn = phi ptr [ %exn.alloc, %lpad.alloc ], [ %exn.copy, %catch.copy ]
%caught = call ptr @__cxa_begin_catch(ptr %exn)
call void @__cxa_end_catch()
br label %return.null

return.null:
ret ptr null
}

define linkonce_odr hidden void @__clang_call_terminate(ptr noundef %0) local_unnamed_addr #4 comdat {
%2 = tail call ptr @__cxa_begin_catch(ptr %0) #13
tail call void @_ZSt9terminatev() #15
unreachable
}

define linkonce_odr void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm(ptr noundef nonnull align 8 dereferenceable(32) %this, i64 noundef %__pos, i64 noundef %__len1, ptr noundef %__s, i64 noundef %__len2) local_unnamed_addr #0 comdat align 2 personality ptr @__gxx_personality_v0 {
entry:
%lenptr = getelementptr inbounds i8, ptr %this, i64 8
%ssoptr = getelementptr inbounds i8, ptr %this, i64 16
%oldlen = load i64, ptr %lenptr, align 8
%oldptr = load ptr, ptr %this, align 8
%issso = icmp eq ptr %oldptr, %ssoptr
br i1 %issso, label %cap.sso, label %cap.heap

cap.sso:
br label %cap.ready

cap.heap:
%heapcap = load i64, ptr %ssoptr, align 8
br label %cap.ready

cap.ready:
%oldcap = phi i64 [ 15, %cap.sso ], [ %heapcap, %cap.heap ]
%removed.end = add i64 %__pos, %__len1
%suffixlen = sub i64 %oldlen, %removed.end
%delta = sub i64 %__len2, %__len1
%newlen = add i64 %oldlen, %delta
%too.large = icmp slt i64 %newlen, 0
br i1 %too.large, label %throw.length, label %choose.capacity

throw.length:
tail call void @_ZSt20__throw_length_errorPKc(ptr noundef nonnull @.str.4) #14
unreachable

choose.capacity:
%needs.growth = icmp ugt i64 %newlen, %oldcap
%doublecap = shl i64 %oldcap, 1
%below.double = icmp ult i64 %newlen, %doublecap
%use.double = and i1 %needs.growth, %below.double
%double.too.large = icmp ugt i64 %doublecap, 9223372036854775807
%capped.double = select i1 %double.too.large, i64 9223372036854775807, i64 %doublecap
%newcap = select i1 %use.double, i64 %capped.double, i64 %newlen
%allocsize = add i64 %newcap, 1
%alloc.invalid = icmp slt i64 %allocsize, 0
br i1 %alloc.invalid, label %throw.alloc, label %allocate

throw.alloc:
tail call void @_ZSt17__throw_bad_allocv() #17
unreachable

allocate:
%newptr = tail call noalias noundef nonnull ptr @_Znwm(i64 noundef %allocsize) #18
%hasprefix = icmp ne i64 %__pos, 0
br i1 %hasprefix, label %copy.prefix, label %insert.check

copy.prefix:
tail call void @llvm.memcpy.p0.p0.i64(ptr nonnull align 1 %newptr, ptr nonnull align 1 %oldptr, i64 %__pos, i1 false)
br label %insert.check

insert.check:
%snonnull = icmp ne ptr %__s, null
%insert.nonempty = icmp ne i64 %__len2, 0
%copyinsert = and i1 %snonnull, %insert.nonempty
br i1 %copyinsert, label %copy.insert, label %suffix.check

copy.insert:
%insertdst = getelementptr inbounds i8, ptr %newptr, i64 %__pos
tail call void @llvm.memcpy.p0.p0.i64(ptr nonnull align 1 %insertdst, ptr nonnull align 1 %__s, i64 %__len2, i1 false)
br label %suffix.check

suffix.check:
%hassuffix = icmp ne i64 %suffixlen, 0
br i1 %hassuffix, label %copy.suffix, label %dispose

copy.suffix:
%suffixdst.base = getelementptr inbounds i8, ptr %newptr, i64 %__pos
%suffixdst = getelementptr inbounds i8, ptr %suffixdst.base, i64 %__len2
%suffixsrc = getelementptr inbounds i8, ptr %oldptr, i64 %removed.end
tail call void @llvm.memcpy.p0.p0.i64(ptr nonnull align 1 %suffixdst, ptr nonnull align 1 %suffixsrc, i64 %suffixlen, i1 false)
br label %dispose

dispose:
br i1 %issso, label %install, label %free.old

free.old:
%oldallocsize = add i64 %oldcap, 1
tail call void @_ZdlPvm(ptr noundef %oldptr, i64 noundef %oldallocsize) #16
br label %install

install:
store ptr %newptr, ptr %this, align 8
store i64 %newcap, ptr %ssoptr, align 8
ret void
}

define linkonce_odr void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7reserveEm(ptr noundef nonnull align 8 dereferenceable(32) %this, i64 noundef %__res) local_unnamed_addr #0 comdat align 2 personality ptr @__gxx_personality_v0 {
entry:
%dataptr = load ptr, ptr %this, align 8
%lenptr = getelementptr inbounds i8, ptr %this, i64 8
%ssoptr = getelementptr inbounds i8, ptr %this, i64 16
%issso = icmp eq ptr %dataptr, %ssoptr
br i1 %issso, label %cap.sso, label %cap.heap

cap.sso:
br label %cap.ready

cap.heap:
%heapcap = load i64, ptr %ssoptr, align 8
br label %cap.ready

cap.ready:
%capacity = phi i64 [ 15, %cap.sso ], [ %heapcap, %cap.heap ]
%enough = icmp ule i64 %__res, %capacity
br i1 %enough, label %return, label %grow

grow:
%len = load i64, ptr %lenptr, align 8
%delta = sub i64 %__res, %len
tail call void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm(ptr noundef nonnull align 8 dereferenceable(32) %this, i64 noundef %len, i64 noundef 0, ptr noundef null, i64 noundef %delta)
%newptr = load ptr, ptr %this, align 8
%nulpos = getelementptr inbounds i8, ptr %newptr, i64 %len
store i8 0, ptr %nulpos, align 1
br label %return

return:
ret void
}

declare i32 @__gxx_personality_v0(...)
declare noundef ptr @_Z16copy_to_c_stringRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(32)) local_unnamed_addr #2
declare ptr @__cxa_begin_catch(ptr) local_unnamed_addr
declare void @__cxa_end_catch() local_unnamed_addr
declare void @_ZSt20__throw_length_errorPKc(ptr noundef) local_unnamed_addr #3
declare void @_ZSt9terminatev() local_unnamed_addr #5
declare void @_ZSt17__throw_bad_allocv() local_unnamed_addr #6
declare noundef nonnull ptr @_Znwm(i64 noundef) local_unnamed_addr #7
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #8
declare void @_ZdlPvm(ptr noundef, i64 noundef) local_unnamed_addr #9
declare void @llvm.assume(i1 noundef) #10

attributes #0 = { mustprogress uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { cold noreturn "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { noinline noreturn nounwind uwtable "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { cold nofree noreturn }
attributes #6 = { noreturn "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #7 = { nobuiltin allocsize(0) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #8 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #9 = { nobuiltin nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #10 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write) }
attributes #13 = { nounwind }
attributes #14 = { cold noreturn }
attributes #15 = { noreturn nounwind }
attributes #16 = { builtin nounwind }
attributes #17 = { noreturn }
attributes #18 = { builtin allocsize(0) }
attributes #19 = { alwaysinline mustprogress nounwind memory(none) }
attributes #20 = { alwaysinline mustprogress nounwind }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}
!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
