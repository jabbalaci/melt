fn main()
{
    let lst = vec!["2", "0", "1", "9"];
    let result: Vec<i32> = lst.iter().map(|s| s.parse().unwrap()).collect();
    for n in result.iter() {
        print!("{}", n);
    }
    println!();
}
