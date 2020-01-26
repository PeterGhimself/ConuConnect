const randodando = [
  [
    {
      course: "COMP 445",
      startTime: "13:15",
      endTime: "14:30"
    }
  ],
  [
    {
      course: "COMP 425",
      startTime: "15:30",
      endTime: "17:30"
    },
    {
      course: "COMP 425",
      startTime: "17:45",
      endTime: "20:15"
    }
  ],
  [
    {
      course: "COMP 445",
      startTime: "11:10",
      endTime: "13:00"
    },
    {
      course: "COMP 445",
      startTime: "13:15",
      endTime: "14:30"
    }
  ],
  [
    {
      course: "ENCS 393",
      startTime: "17:45",
      endTime: "20:15"
    }
  ],
  []
];

const timeToFrac = time => {
  const timeSplit = time.split(":");
  return (parseInt(timeSplit[0]) - 7) + (parseInt(timeSplit[1]) / 60);
};

const loadSchedule = (schedule, $container) => {
  const heightPx = 700;
  const heightHours = 16;
  const pxPerHour = heightPx / heightHours;
  $container.html(schedule.map((dayOfWeek, dowi) => {
    let content = "";
    dayOfWeek.forEach(({ course, startTime, endTime }, i) => {
      const startTimeFrac = timeToFrac(startTime);
      const endTimeFrac = timeToFrac(endTime);
      const paddingTop = i === 0 ? (startTimeFrac * pxPerHour) : 0;
      content += `<div class="courseBlock" style="
        height: ${(endTimeFrac - startTimeFrac) * pxPerHour}px; 
        margin-top: ${paddingTop}px">
        <div><div>${course}</div><div>${startTime} - ${endTime}</div></div>
      </div>`;
      if(i !== dayOfWeek.length - 1) {
        content += `<div class="breakBlock" style="
          height: ${(timeToFrac(dayOfWeek[i + 1].startTime) - endTimeFrac) * pxPerHour}px;
        ">
          <div><input type="radio" name="selectedBreak" value="${`${dowi}:${startTime}`}"></div>
        </div>`
      }
    });
    return `<div class="dayColumn">${content}</div>`;
  }));
};

let searchResults;

const loadSearchResults = results => {
  searchResults = results;
  const $searchResultsContainer = $("#searchResultsContainer");
  $searchResultsContainer.empty();
  results.forEach(({ studentInfo, rankScores }, i) => {
    $searchResultsContainer.append(`
      <div class="searchResultItem ${i}" onclick="() => { showScheduleModal(${i}) }">
        <div>${studentInfo.name}</div>
        <div>${studentInfo.email}</div>
        <div>${studentInfo.ID}</div>
        <div>${studentInfo.program}</div>
      </div>
    `);
    $(`.searchResultItem.${i}`).on("click", () => {
      showScheduleModal(i)
    });
  });
};

const showScheduleModal = index => {
  $("body").append(`
    <div id="scheduleModal"
         style="position: absolute; height: 100%; width: 100%; left: 0; top: 0; background-color: rgba(0, 0, 0, 0.3);">
         <div style="height: 700px; 
                     width: 500px; 
                     margin: auto; 
                     background-color: white; 
                     border: 1px solid grey;
                     display: flex;
                     flex-grow: 1;
                     padding: 8px;"></div>
    </div>
  `);
  $("#scheduleModal").on("click", () => {
    $('#scheduleModal').remove();
  });
  console.log(searchResults);
  loadSchedule(searchResults[index].studentInfo.schedule, $("#scheduleModal > div"));
};

// $("input:radio[name ='selectedBreak']:checked").val();